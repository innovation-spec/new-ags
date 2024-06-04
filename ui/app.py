import streamlit as st
from api.client import ApiClient

st.set_page_config(page_title="Agasthya AI Retail Demo", page_icon="🛒", layout="wide")
api = ApiClient()
st.title("Agasthya Multi-tenant Recommendation + Inventory Demo")
st.caption("Local Docker Compose control console — deterministic backend, optional OpenAI explanation")
health = api.health()
if isinstance(health, dict) and health.get("status") == "ok":
    c1, c2 = st.columns(2)
    c1.success("FastAPI connected")
    c2.info("OpenAI enabled" if health.get("openai_enabled") else "OpenAI disabled — add OPENAI_API_KEY when needed")
else:
    st.error(f"Backend unavailable: {health}")
st.markdown("Use the sidebar pages to explore AI recommendations, execution runs, and failure/concurrency demonstrations.")
