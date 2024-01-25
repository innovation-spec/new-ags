import streamlit as st
from api.client import ApiClient
from components.cards import render_error

st.title("Agent Runs")
api = ApiClient()
tenants = api.tenants()
