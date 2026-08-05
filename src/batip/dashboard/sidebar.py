import streamlit as st


def show_sidebar():

    with st.sidebar:

        st.title("Settings")

        symbol = st.selectbox(
            "Index",
            [
                "BANKNIFTY",
                "NIFTY",
                "FINNIFTY",
                "MIDCPNIFTY",
            ],
        )

        expiry = st.selectbox(
            "Expiry",
            [
                "Current Week",
                "Next Week",
                "Monthly",
            ],
        )

        refresh = st.button("🔄 Refresh")

    return symbol, expiry, refresh