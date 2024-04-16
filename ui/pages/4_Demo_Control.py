import streamlit as st
from api.client import ApiClient
from components.cards import render_error

st.title("Demo Control")
api = ApiClient()
tenants = api.tenants()
if render_error(tenants) or not tenants: st.stop()
labels = {f"{x['name']} ({x['id']})": x["id"] for x in tenants}
tenant_id = labels[st.selectbox("Tenant", list(labels))]
customers = api.customers(tenant_id, 20)
customer_id = customers[0]["id"] if isinstance(customers, list) and customers else None

c1,c2 = st.columns(2)
with c1:
    st.subheader("Concurrency")
    if st.button("Run inventory oversell test (100 requests)"):
        result = api.demo("inventory-race", tenant_id=tenant_id, stock=5, attempts=100)
        if not render_error(result): st.json(result)
    if st.button("Run shared-state conflict test (100 patches)"):
        result = api.demo("state-conflict", tenant_id=tenant_id, operations=100)
        if not render_error(result): st.json(result)
with c2:
    st.subheader("External failure simulation")
    scenario = st.selectbox("Failure scenario", ["timeout", "rate_limit", "malformed", "conflict", "normal"])
    if st.button("Run external-data flow"):
        result = api.demo("external-failure", tenant_id=tenant_id, query="DEMO-SKU", scenario=scenario)
        if not render_error(result): st.json(result)

st.subheader("Recommendation + memory")
if customer_id and st.button("Generate recommendation demo"):
    result = api.demo("recommendation", tenant_id=tenant_id, customer_id=customer_id, limit=10)
    if not render_error(result): st.json(result)
if st.button("Run memory pruning"):
    result = api.demo("memory-prune", tenant_id=tenant_id)
    if not render_error(result): st.json(result)

st.subheader("PPO source-selection research")
st.caption("PPO runs in shadow mode only. Deterministic credibility rules remain authoritative.")
ppo_iterations = st.slider("PPO training iterations", min_value=10, max_value=120, value=60, step=10)
if st.button("Run PPO shadow evaluation"):
    result = api.demo("ppo-shadow", seed=42, iterations=ppo_iterations)
