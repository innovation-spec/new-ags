import streamlit as st
from api.client import ApiClient
from components.cards import tenant_customer_select, render_error, render_product

st.title("Recommendation Explorer")
api = ApiClient()
tenant_id, customer_id = tenant_customer_select(api, "recs")
limit = st.slider("Top K", 1, 20, 10)
if st.button("Generate recommendations", type="primary"):
    result = api.recommend(tenant_id, customer_id, limit)
    if not render_error(result):
