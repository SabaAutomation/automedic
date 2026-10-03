from pathlib import Path
from workflows.demo_workflow import run_workflow

LOG = Path("logs/errors.log")

def read_error_log() -> str:
    """Read the latest error from the failed workflow."""
    if not LOG.exists() or not LOG.read_text().strip():
        return "No errors found."
    return LOG.read_text()

def retry_workflow() -> str:
    """Retry the failed workflow once. Returns 'success' or 'failed'."""
    return run_workflow(simulate_failure=False)

def send_notification(message: str) -> str:
    """Send the user a plain-English report about what happened."""
    print(f"\nNOTIFICATION: {message}\n")
    return "sent"