import streamlit as st


def show_metrics():

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Spot", "--")

    c2.metric("Future", "--")

    c3.metric("PCR", "--")

    c4.metric("AI Score", "--")