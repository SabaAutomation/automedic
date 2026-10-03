from pathlib import Path

LOG = Path("logs/errors.log")

def run_workflow(simulate_failure: bool = True) -> str:
    LOG.parent.mkdir(exist_ok=True)
    if simulate_failure:
        LOG.write_text("ERROR: Google Sheets API timeout at step 3\n")
        return "failed"
    LOG.write_text("")
    return "success"