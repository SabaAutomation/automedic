import sys
from pathlib import Path

# Let the dashboard import the agent code from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from agent.agent import run_agent
from agent.incidents import load_incidents
from workflows.demo_workflow import FAILURES, start_failure

st.set_page_config(page_title="AutoMedic", page_icon="🩺", layout="wide")

st.title("🩺 AutoMedic")
st.caption("A self-healing automation agent. It diagnoses failed workflows, fixes them, or escalates to a human.")

# ---------- Sidebar: trigger a failure live ----------
with st.sidebar:
    st.header("Break a workflow")
    kind = st.selectbox("Failure type", list(FAILURES.keys()))
    st.code(FAILURES[kind], language=None)
    if st.button("Run AutoMedic", type="primary", use_container_width=True):
        with st.spinner("AutoMedic is investigating..."):
            start_failure(kind)
            run_agent(
                "A workflow just failed. Investigate, fix it if safe, and report back.",
                kind=kind,
            )
        st.success("Incident handled.")

incidents = load_incidents()

# ---------- Summary numbers ----------
total = len(incidents)
fixed = sum(1 for i in incidents if i["outcome"] == "auto-fixed")
escalated = total - fixed

c1, c2, c3, c4 = st.columns(4)
c1.metric("Incidents", total)
c2.metric("Auto-fixed", fixed)
c3.metric("Escalated to human", escalated)
c4.metric("Auto-fix rate", f"{round(100 * fixed / total)}%" if total else "-")

st.divider()

if not incidents:
    st.info("No incidents yet. Pick a failure in the sidebar and click **Run AutoMedic**.")
    st.stop()

# ---------- Incident table ----------
st.subheader("Incident history")
rows = [
    {
        "Time": i["time"],
        "Failure": i["kind"],
        "Outcome": ("✅ " if i["outcome"] == "auto-fixed" else "🙋 ") + i["outcome"],
        "Steps": len(i["steps"]),
        "Seconds": i["seconds"],
    }
    for i in reversed(incidents)
]
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ---------- Incident details ----------
st.subheader("What the agent did")
for n, inc in enumerate(reversed(incidents[-10:])):
    icon = "✅" if inc["outcome"] == "auto-fixed" else "🙋"
    with st.expander(f"{icon} {inc['time']}  |  {inc['kind']}", expanded=(n == 0)):
        st.markdown(f"**Error:** `{inc['error']}`")
        for k, step in enumerate(inc["steps"], start=1):
            st.markdown(f"{k}. **{step['tool']}** → {step['result']}")
        st.markdown(f"**Report sent:** {inc['message']}")