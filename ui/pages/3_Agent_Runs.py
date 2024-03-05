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
