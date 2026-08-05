import streamlit as st

from batip.dashboard.header import show_header
from batip.dashboard.layout import show_layout
from batip.dashboard.metrics import show_metrics
from batip.dashboard.sidebar import show_sidebar
from batip.dashboard.theme import load_theme


def run_dashboard():

    st.set_page_config(
        page_title="BATIP PRO",
        page_icon="📈",
        layout="wide",
    )

    load_theme()

    symbol, expiry, refresh = show_sidebar()

    show_header()

    st.caption(f"Selected Index: **{symbol}** | Expiry: **{expiry}**")

    if refresh:
        st.toast("Refreshing market data...")

    show_metrics()

    st.divider()

    show_layout()