import streamlit as st
from api.client import ApiClient
from components.cards import tenant_customer_select, render_error, render_product

st.title("AI Assistant")
api = ApiClient()
tenant_id, customer_id = tenant_customer_select(api, "assistant")
if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])
prompt = st.chat_input("Ask for product recommendations or customer-aware retail help")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.status("Running backend recommendations and agent tools...", expanded=True) as status:
            result = api.chat(tenant_id, customer_id, prompt)
            if render_error(result): status.update(label="Request failed", state="error")
            else:
