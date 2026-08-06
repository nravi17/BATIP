"""
Dashboard Metrics
"""

import streamlit as st


def render_metrics(data: dict) -> None:
    """Render dashboard metrics."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Spot",
            value=f"{data['chain'].spot_price:,.2f}",
            delta="+125.40",
        )

    with col2:
        st.metric(
            label="PCR",
            value=f"{data['pcr'].value:.2f}",
        )

    with col3:
        st.metric(
            label="Max Pain",
            value=data["max_pain"].strike,
        )

    with col4:
        st.metric(
            label="Support",
            value=data["support"].support,
        )