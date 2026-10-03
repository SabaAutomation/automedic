# AutoMedic

A self-healing automation agent. When a workflow fails, AutoMedic reads the error, diagnoses the cause, takes a safe action, and sends a plain-English report.

Runs 100% free and locally using [Ollama](https://ollama.com).

## How it works

1. A workflow runs and fails.
2. The agent reads the error log.
3. It decides which action to take.
4. It sends a notification explaining what happened.
5. It stops once the incident is handled.

## Tools the agent can use

| Tool | Purpose |
|---|---|
| `read_error_log` | Reads the latest workflow error |
| `retry_workflow` | Re-runs the failed workflow |
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
python main.py
```

## Example output

```
[tool] read_error_log -> ERROR: Google Sheets API timeout at step 3
[tool] retry_workflow -> success
NOTIFICATION: The Google Sheets API timeout has been retried and succeeded.
AutoMedic: incident handled.
```

## Challenges and lessons

- Small coder models sometimes write tool calls as plain text instead of real tool calls. I added a parser that detects this and runs the tool anyway.
- The agent originally kept going after reporting. I added a stop condition so each incident is handled once.
- The model is set in `.env`, so it can be swapped with one line.

## Roadmap

- [ ] Multiple failure types (timeout, bad data, expired token, missing field)
- [ ] Escalate to a human when a fix is unsafe
- [ ] Telegram notifications
- [ ] Real n8n workflows
- [ ] Streamlit dashboard

## Tech

Python, Ollama (Qwen 2.5 Coder), Git