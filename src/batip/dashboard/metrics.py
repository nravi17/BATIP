"""
Professional Dashboard Metrics
"""

from __future__ import annotations

import streamlit as st


def metric_card(
    title: str,
    value,
    delta: str = "",
    color: str = "#1E293B",
) -> None:
    """
    Render a professional metric card.
    """

    st.markdown(
        f"""
<div style="
background:{color};
padding:18px;
border-radius:14px;
border:1px solid #334155;
box-shadow:0 3px 8px rgba(0,0,0,.35);
">

<div style="
font-size:15px;
color:#CBD5E1;
font-weight:600;
">
{title}
</div>

<div style="
font-size:40px;
font-weight:700;
color:white;
padding-top:10px;
">
{value}
</div>

<div style="
color:#22C55E;
font-size:15px;
font-weight:600;
padding-top:6px;
">
{delta}
</div>

</div>
""",
        unsafe_allow_html=True,
    )


def render_metrics(data: dict) -> None:
    """
    Render dashboard KPI cards.
    """

    chain = data["chain"]

    pcr = data["pcr"]

    max_pain = data["max_pain"]

    support = data["support"]

    cols = st.columns(4)

    with cols[0]:
        metric_card(
            "📈 Spot",
            f"{chain.spot_price:,.2f}",
            "▲ +125.40",
            "#1E293B",
        )

    with cols[1]:
        metric_card(
            "🟡 PCR",
            f"{pcr.value:.2f}",
            "Bullish",
            "#1F2937",
        )

    with cols[2]:
        metric_card(
            "🎯 Max Pain",
            max_pain.strike,
            "Major OI",
            "#1F2937",
        )

    with cols[3]:
        metric_card(
            "🟢 Support",
            support.support,
            "Strong",
            "#1F2937",
        )