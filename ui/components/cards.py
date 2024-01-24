import streamlit as st

def render_error(payload):
    if isinstance(payload, dict) and payload.get("ok") is False:
        st.error(payload.get("error", "Request failed"))
        return True
    return False

