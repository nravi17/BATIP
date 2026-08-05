import streamlit as st


def run_dashboard():

    st.set_page_config(
        page_title="BATIP",
        page_icon="📈",
        layout="wide"
    )

    st.title("📈 BATIP")

    st.subheader("BankNifty AI Trading Intelligence Platform")

    st.success("Sprint 1 Successfully Running")

    c1, c2, c3 = st.columns(3)

    c1.metric("Spot", "--")

    c2.metric("PCR", "--")

    c3.metric("AI Score", "--")

    st.divider()

    st.info("Welcome to BATIP 🚀")