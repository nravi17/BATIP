"""
Dashboard Header
"""

import streamlit as st


def render_header() -> None:

    st.set_page_config(
        page_title="BATIP Pro",
        layout="wide",
    )

    st.title("📈 BATIP Pro")

    st.caption(
        "BankNifty Analytics & Trading Intelligence Platform"
    )