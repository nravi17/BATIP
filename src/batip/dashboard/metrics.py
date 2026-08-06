"""
Dashboard Metrics
"""

import streamlit as st


def render_metrics(data: dict) -> None:
    """Render top metrics."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Spot",
            f"{data['chain'].spot_price:,.2f}",
        )

    with col2:
        st.metric(
            "PCR",
            f"{data['pcr'].value:.2f}",
        )

    with col3:
        st.metric(
            "Max Pain",
            data["max_pain"].strike,
        )

    with col4:
        st.metric(
            "Support",
            data["support"].support,
        )