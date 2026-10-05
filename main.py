import sys
from workflows.demo_workflow import start_failure, FAILURES
from agent.agent import run_agent

kind = sys.argv[1] if len(sys.argv) > 1 else "timeout"
if kind not in FAILURES:
    print("Choose one of:", ", ".join(FAILURES))
    sys.exit(1)

print(f"Running workflow... (simulating: {kind})")
print("Result:", start_failure(kind))

print("\nAutoMedic is investigating...\n")
run_agent("A workflow just failed. Investigate, fix it if safe, and report back.", kind=kind)