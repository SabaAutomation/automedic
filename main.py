from workflows.demo_workflow import run_workflow
from agent.agent import run_agent

print("Running workflow...")
print("Result:", run_workflow(simulate_failure=True))

print("\nAutoMedic is investigating...\n")
run_agent("A workflow just failed. Investigate, fix it, and report back.")