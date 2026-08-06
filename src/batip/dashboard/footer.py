"""
Dashboard Footer
"""

import streamlit as st


def render_footer() -> None:

    st.divider()

    st.caption(
        "BATIP v0.4.1 | Built with ❤️ using Streamlit"
    )