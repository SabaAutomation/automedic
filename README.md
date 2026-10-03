# AutoMedic

A self-healing automation agent. When a workflow fails, AutoMedic reads the error, diagnoses the cause, picks the right fix, and sends a plain-English report. If a fix isn't safe, it escalates to a human instead of guessing.

Runs 100% free and locally using [Ollama](https://ollama.com).

## How it works

1. A workflow fails.
2. The code reads the error log (always step 1).
3. The agent chooses the fix based on the error type.
4. It runs the fix and retries the workflow.
5. It sends a notification explaining what happened, then stops.

## Failure types handled

| Failure | Agent's action |
|---|---|
| API timeout | `retry_workflow` |
| Invalid date format | `clean_data`, then `retry_workflow` |
| Expired token (401) | `refresh_token`, then `retry_workflow` |
| Missing required field | `escalate_to_human` (no guessing) |

## Tools

| Tool | Purpose |
|---|---|
| `read_error_log` | Reads the latest workflow error |
| `retry_workflow` | Re-runs the workflow |
| `clean_data` | Fixes badly formatted data |
| `refresh_token` | Refreshes an expired access token |
| `escalate_to_human` | Hands off when a fix is unsafe |
| `send_notification` | Reports the outcome to the user |

## Setup

```
git clone https://github.com/SabaAutomation/automedic.git
cd automedic
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
ollama pull qwen2.5-coder:7b
python main.py timeout
```

Try the other failures: `bad_data`, `expired_token`, `missing_field`.

## Example output

```
[tool] read_error_log -> ERROR: 401 Unauthorized - access token expired at step 1
[tool] refresh_token -> Access token refreshed
[tool] retry_workflow -> success
NOTIFICATION: Workflow failed due to expired access token. Token has been refreshed and workflow retried successfully.
AutoMedic: incident handled.
```

## Challenges and lessons

- Small coder models sometimes write tool calls as plain text. I added a parser that detects this and runs the tool anyway.
- A 7B model sometimes skipped the first step, so the code now reads the error log itself and gives it to the model.
- The model could dump a whole plan at once, so the loop now runs one tool per step.
- If the model replies with text instead of a tool call, the agent nudges it up to twice.
- The model is set in `.env`, so it can be swapped with one line.

## Roadmap

- [x] Multiple failure types
- [x] Escalate to a human when a fix is unsafe
- [ ] Block notifications until a fix or escalation has run
- [ ] Telegram notifications
- [ ] Real n8n workflows
- [ ] Streamlit dashboard

## Tech

Python, Ollama (Qwen 2.5 Coder), Git