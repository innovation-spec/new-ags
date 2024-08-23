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
        a,b,c = st.columns(3)
        a.metric("Model", result.get("model_name"))
        b.metric("Version", result.get("model_version"))
        c.metric("Returned", len(result.get("items", [])))
        with st.expander("Customer feature/profile snapshot"):
            st.json(result.get("profile", {}))
        for item in result.get("items", []): render_product(item)
st.subheader("Model registry")
models = api.models()
if not render_error(models): st.json(models, expanded=False)
