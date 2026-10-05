import json
from datetime import datetime
from pathlib import Path

FILE = Path("logs/incidents.jsonl")


def record_incident(incident: dict):
    """Append one incident to the history file."""
    FILE.parent.mkdir(exist_ok=True)
    incident["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(incident) + "\n")


def load_incidents() -> list:
    """Read all saved incidents, oldest first."""
    if not FILE.exists():
        return []
    incidents = []
    for line in FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                incidents.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return incidents