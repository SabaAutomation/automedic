import json
import re
import ollama
from agent.config import MODEL
from agent import tools

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


def run_agent(goal: str, max_steps: int = 10):
    # Step 1 is always the same, so the code does it instead of the model.
    error = tools.read_error_log()
    print(f"[tool] read_error_log -> {error.strip()}")

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{goal}\n\nThe error log says: {error}"},
    ]
    nudges = 0
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
            print(msg.content)
            return

        name, args = calls[0]
        fn = AVAILABLE.get(name)
        try:
            result = fn(**args) if fn else "Unknown tool"
        except TypeError as e:
            result = f"Bad arguments: {e}"
        print(f"[tool] {name} -> {result}")
        messages.append({"role": "tool", "tool_name": name, "content": str(result)})

        if name == "send_notification":
            print("AutoMedic: incident handled.")
            return

    print("AutoMedic: stopped after max steps without finishing.")