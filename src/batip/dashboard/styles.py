import streamlit as st


def load_styles() -> None:

    st.markdown(
        """
        <style>

        .block-container{
            padding-top:1rem;
            padding-bottom:1rem;
        }

        div[data-testid="stMetric"]{
            border-radius:12px;
            padding:14px;
            background:#1f2937;
            border:1px solid #374151;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )