"""
BATIP Global Styles
"""

from __future__ import annotations

import streamlit as st


def load_styles() -> None:
    """
    Global BATIP theme.
    """

    st.markdown(
        """
<style>

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

div[data-testid="stMetric"]{
    background:#1E293B;
    border-radius:14px;
    padding:12px;
}

table{
    font-size:15px;
}

</style>
""",
        unsafe_allow_html=True,
    )