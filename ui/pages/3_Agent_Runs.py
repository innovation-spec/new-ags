import streamlit as st
from api.client import ApiClient
from components.cards import render_error

st.title("Agent Runs")
api = ApiClient()
tenants = api.tenants()
if render_error(tenants) or not tenants: st.stop()
labels = {f"{x['name']} ({x['id']})": x["id"] for x in tenants}
tenant_id = labels[st.selectbox("Tenant", list(labels))]
runs = api.runs(tenant_id)
if render_error(runs): st.stop()
if not runs:
    st.info("No agent runs yet. Use AI Assistant first.")
else:
    run_labels = {f"{r['status']} · {r['id'][:8]} · {r.get('input_text','')[:50]}": r["id"] for r in runs}
    run_id = run_labels[st.selectbox("Run", list(run_labels))]
    run = api.run(tenant_id, run_id)
    if not render_error(run):
        st.json({k:v for k,v in run.items() if k != "events"}, expanded=False)
        st.subheader("Execution timeline")
        for event in run.get("events", []):
            with st.container(border=True):
                st.markdown(f"**{event['event_type']}** — {event['agent']}")
                if event.get("payload"): st.json(event["payload"], expanded=False)
