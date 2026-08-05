import streamlit as st
from datetime import datetime


def show_header():

    left, right = st.columns([4, 1])

    with left:
        st.title("📈 BATIP PRO")
        st.caption("BankNifty AI Trading Intelligence Platform")

    with right:
        st.metric(
            "Last Refresh",
            datetime.now().strftime("%H:%M:%S"),
        )

    st.divider()