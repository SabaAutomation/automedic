import json
import re
import time
import ollama
from agent.config import MODEL
from agent import tools
from agent.incidents import record_incident

TOOLS = [
    tools.read_error_log,
    tools.retry_workflow,
    tools.clean_data,
    tools.refresh_token,
    tools.escalate_to_human,
    tools.send_notification,
]
AVAILABLE = {f.__name__: f for f in TOOLS}

SYSTEM = (
    "You are AutoMedic, an agent that fixes failed automations. "
    "You MUST act only by calling tools. Never write explanations, comments or plans. "
    "Call exactly one tool at a time and wait for its result. "
    "You will be given the error. Choose the fix: "
    "timeout error -> retry_workflow. "
    "invalid date or format error -> clean_data, then retry_workflow. "
    "401 or expired token error -> refresh_token, then retry_workflow. "
    "missing required field error -> call escalate_to_human, do NOT retry. "
    "If retry_workflow returns failed, call escalate_to_human. "
    "You cannot send_notification until the problem is fixed or escalated. "
    "Final step: call send_notification with a short report of what failed, "
    "what you did, and the result. Use the real values from the tool results."
)


def extract_text_tool_call(content: str):
    """Find the first tool call written as JSON text, even if surrounded by other text."""
    if not content:
        return None
    for match in re.finditer(r"\{.*?\}\s*\}|\{.*?\}", content, re.DOTALL):
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("name") in AVAILABLE:
            return data["name"], data.get("arguments") or {}
    return None


def run_agent(goal: str, kind: str = "unknown", max_steps: int = 10) -> dict:
    started = time.time()

    # Step 1 is always the same, so the code does it instead of the model.
    error = tools.read_error_log()
    print(f"[tool] read_error_log -> {error.strip()}")
    steps = [{"tool": "read_error_log", "result": error.strip()}]

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{goal}\n\nThe error log says: {error}"},
    ]

    nudges = 0
    fixed = False
    escalated = False
    notified = False
    message = ""

    for _ in range(max_steps):
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        msg = response.message
        messages.append(msg)

        calls = []
        if msg.tool_calls:
            calls = [(c.function.name, dict(c.function.arguments)) for c in msg.tool_calls]
        else:
            parsed = extract_text_tool_call(msg.content)
            if parsed:
                calls = [parsed]

        if not calls:
            if nudges < 2:
                nudges += 1
                messages.append({
                    "role": "user",
                    "content": "You did not call a tool. Call the next tool now. No text.",
                })
                continue
            break

        name, args = calls[0]

        # Safety guard: no notification until the incident is fixed or escalated.
        if name == "send_notification" and not (fixed or escalated):
            result = "BLOCKED: fix the problem or call escalate_to_human before notifying."
            print(f"[guard] {result}")
            steps.append({"tool": "guard", "result": result})
            messages.append({"role": "tool", "tool_name": name, "content": result})
            continue

        fn = AVAILABLE.get(name)
        try:
            result = fn(**args) if fn else "Unknown tool"
        except TypeError as e:
            result = f"Bad arguments: {e}"
        print(f"[tool] {name} -> {result}")
        steps.append({"tool": name, "result": str(result)})
        messages.append({"role": "tool", "tool_name": name, "content": str(result)})

        if name == "retry_workflow" and result == "success":
            fixed = True
        if name == "escalate_to_human":
            escalated = True
        if name == "send_notification":
            message = str(args.get("message", ""))
            notified = True
            break

    # Fallback: if the agent never finished, a human must take over.
    if not notified:
        if not (fixed or escalated):
            reason = "AutoMedic could not resolve this incident automatically."
            tools.escalate_to_human(reason)
            steps.append({"tool": "escalate_to_human", "result": "escalated (fallback)"})
            escalated = True
        message = "Incident handled." if fixed else "A human has been alerted."
        tools.send_notification(message)
        steps.append({"tool": "send_notification", "result": "sent (fallback)"})

    print("AutoMedic: incident handled.")

    incident = {
        "kind": kind,
        "error": error.strip(),
        "steps": steps,
        "outcome": "auto-fixed" if fixed else "escalated",
        "message": message,
        "seconds": round(time.time() - started, 1),
    }
    record_incident(incident)
    return incident