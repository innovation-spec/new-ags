import streamlit as st
from api.client import ApiClient

st.set_page_config(page_title="Agasthya AI Retail Demo", page_icon="🛒", layout="wide")
api = ApiClient()
st.title("Agasthya Multi-tenant Recommendation + Inventory Demo")
st.caption("Local Docker Compose control console — deterministic backend, optional OpenAI explanation")
health = api.health()
