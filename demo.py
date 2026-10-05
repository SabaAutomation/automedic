import time
from workflows.demo_workflow import start_failure
from agent.agent import run_agent

GOAL = "A workflow just failed. Investigate, fix it if safe, and report back."


def banner(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")
    time.sleep(2)


banner("DEMO 1: AutoMedic FIXES a failure (expired token)")
print("Workflow:", start_failure("expired_token"))
time.sleep(1)
run_agent(GOAL, kind="expired_token")

time.sleep(3)

banner("DEMO 2: AutoMedic ESCALATES (missing required field)")
print("Workflow:", start_failure("missing_field"))
time.sleep(1)
run_agent(GOAL, kind="missing_field")

print("\nDone. Fixed what was safe, handed the rest to a human.")