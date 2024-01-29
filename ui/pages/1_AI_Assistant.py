import streamlit as st
from api.client import ApiClient
from components.cards import tenant_customer_select, render_error, render_product

st.title("AI Assistant")
api = ApiClient()
tenant_id, customer_id = tenant_customer_select(api, "assistant")
