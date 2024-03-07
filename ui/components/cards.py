import streamlit as st

def render_error(payload):
    if isinstance(payload, dict) and payload.get("ok") is False:
        st.error(payload.get("error", "Request failed"))
        return True
    return False

def render_product(item: dict):
    with st.container(border=True):
        cols = st.columns([3, 1, 1])
        cols[0].markdown(f"**{item.get('name', item.get('product_id', 'Product'))}**")
        cols[1].metric("Score", f"{float(item.get('score', 0)):.3f}")
        cols[2].metric("Available", item.get("available", "—"))
        st.caption(f"Product: {item.get('product_id')} · {item.get('brand','')} {item.get('category','')} · ${float(item.get('price',0)):.2f}" if item.get("price") is not None else str(item.get("product_id")))
        reasons = item.get("reasons")
