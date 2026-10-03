import json
from pathlib import Path

LOG = Path("logs/errors.log")
STATE = Path("logs/state.json")

FAILURES = {
    "timeout": "ERROR: Google Sheets API timeout at step 3",
    "bad_data": "ERROR: Invalid date format '03/10/2026' in field 'date' at step 2 (expected YYYY-MM-DD)",
    "expired_token": "ERROR: 401 Unauthorized - access token expired at step 1",
    "missing_field": "ERROR: Required field 'customer_email' is missing at step 2",
}

def _save(state: dict):
    LOG.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state))

def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}

def start_failure(kind: str):
    """Simulate a workflow failing in a specific way."""
    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text(FAILURES[kind] + "\n")
    _save({"kind": kind, "data_cleaned": False, "token_refreshed": False})
    return "failed"

def run_workflow() -> str:
    """Re-run the workflow. Succeeds only if the root cause is fixed."""
    state = load_state()
    kind = state.get("kind")
    if kind == "timeout":
        ok = True
    elif kind == "bad_data":
        ok = state.get("data_cleaned", False)
    elif kind == "expired_token":
        ok = state.get("token_refreshed", False)
    else:
        ok = False
    LOG.write_text("" if ok else FAILURES.get(kind, "ERROR: unknown") + "\n")
    return "success" if ok else "failed"

def clean_data():
    state = load_state()
    state["data_cleaned"] = True
    _save(state)
    return "Date reformatted to YYYY-MM-DD"

def refresh_token():
    state = load_state()
    state["token_refreshed"] = True
    _save(state)
    return "Access token refreshed"