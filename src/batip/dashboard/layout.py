import streamlit as st


def show_layout():

    st.subheader("Live Option Chain")

    st.info("Live data module will be connected in Sprint 2.")

    left, right = st.columns(2)

    with left:
        st.subheader("Support & Resistance")

        st.empty()

    with right:
        st.subheader("Strategy Recommendation")

        st.empty()