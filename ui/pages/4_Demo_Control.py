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
