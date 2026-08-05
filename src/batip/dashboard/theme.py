import streamlit as st


def load_theme():
    st.markdown(
        """
        <style>

        .main{
            background-color:#0F172A;
        }

        div[data-testid="stMetric"]{
            background:#1E293B;
            border-radius:12px;
            padding:15px;
            border:1px solid #334155;
        }

        h1,h2,h3{
            color:white;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )