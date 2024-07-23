import streamlit as st
from api.client import ApiClient
from components.cards import tenant_customer_select, render_error, render_product

st.title("Recommendation Explorer")
api = ApiClient()
