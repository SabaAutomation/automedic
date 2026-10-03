from pathlib import Path
from workflows import demo_workflow

LOG = Path("logs/errors.log")

def read_error_log() -> str:
    """Read the latest error from the failed workflow."""
    if not LOG.exists() or not LOG.read_text().strip():
        return "No errors found."
    return LOG.read_text()

def retry_workflow() -> str:
    """Re-run the workflow. Returns 'success' or 'failed'."""
    return demo_workflow.run_workflow()

def clean_data() -> str:
    """Fix bad data, such as a wrongly formatted date. Use for invalid format errors."""
    return demo_workflow.clean_data()

def refresh_token() -> str:
    """Refresh an expired access token. Use for 401 or token expired errors."""
    return demo_workflow.refresh_token()

def escalate_to_human(reason: str) -> str:
    """Use when the problem cannot be fixed safely, for example missing required data."""
    print(f"\nESCALATED TO HUMAN: {reason}\n")
    return "escalated"

def send_notification(message: str) -> str:
    """Send the user a plain-English report about what happened."""
    print(f"\nNOTIFICATION: {message}\n")
    return "sent"