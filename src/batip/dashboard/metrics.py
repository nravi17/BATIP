"""
Dashboard Metrics
"""

from __future__ import annotations

import streamlit as st


def _get_value(data, key, default=None):
    """
    Read a value from either a dictionary or an object.
    """
    if isinstance(data, dict):
        return data.get(key, default)

    return getattr(data, key, default)


def _get_chain(data):
    """
    Get option chain from dashboard data.
    """
    return _get_value(data, "chain")


def _get_nested_value(data, key, attribute, default=0):
    """
    Read a nested value from either dictionaries or objects.
    """
    parent = _get_value(data, key)

    if parent is None:
        return default

    if isinstance(parent, dict):
        return parent.get(attribute, default)

    return getattr(parent, attribute, default)


def _format_number(value, decimals=0):
    """
    Format a numeric value safely.
    """
    try:
        number = float(value)

        if decimals == 0:
            return f"{number:,.0f}"

        return f"{number:,.{decimals}f}"

    except (TypeError, ValueError):
        return "—"


def _apply_metric_css() -> None:
    """
    Apply professional styling to Streamlit metric cards.

    The CSS prevents large numbers from being truncated
    with an ellipsis inside narrow dashboard columns.
    """

    st.markdown(
        """
        <style>

        /* ---------------------------------------------------------
           METRIC CARD
        --------------------------------------------------------- */

        div[data-testid="stMetric"] {
            min-height: 108px;
            padding: 16px 16px 12px 16px;
            border-radius: 14px;
        }

        /* ---------------------------------------------------------
           METRIC LABEL
        --------------------------------------------------------- */

        div[data-testid="stMetricLabel"] {
            white-space: nowrap;
            overflow: visible;
        }

        div[data-testid="stMetricLabel"] p {
            font-size: 0.82rem;
            font-weight: 600;
            white-space: nowrap;
        }

        /* ---------------------------------------------------------
           METRIC VALUE
        --------------------------------------------------------- */

        div[data-testid="stMetricValue"] {
            overflow: visible !important;
            white-space: nowrap !important;
        }

        div[data-testid="stMetricValue"] > div {
            overflow: visible !important;
            white-space: nowrap !important;
            text-overflow: clip !important;
            font-size: clamp(1.45rem, 2.2vw, 2.05rem) !important;
            line-height: 1.15 !important;
            letter-spacing: -0.025em;
        }

        /* ---------------------------------------------------------
           METRIC DELTA
        --------------------------------------------------------- */

        div[data-testid="stMetricDelta"] {
            white-space: nowrap;
            overflow: visible;
        }

        div[data-testid="stMetricDelta"] p {
            font-size: 0.78rem;
        }

        /* ---------------------------------------------------------
           DASHBOARD COLUMNS
        --------------------------------------------------------- */

        div[data-testid="column"] {
            min-width: 0;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(data) -> None:
    """
    Render the main dashboard metric cards.
    """

    # Apply UI styling once per render.
    _apply_metric_css()

    chain = _get_chain(data)

    # ---------------------------------------------------------
    # SPOT
    # ---------------------------------------------------------

    spot_price = 0

    if chain is not None:
        if isinstance(chain, dict):
            spot_price = chain.get("spot_price", 0)
        else:
            spot_price = getattr(chain, "spot_price", 0)

    # ---------------------------------------------------------
    # PCR
    # ---------------------------------------------------------

    pcr_value = _get_nested_value(
        data,
        "pcr",
        "value",
        0,
    )

    # ---------------------------------------------------------
    # MAX PAIN
    # ---------------------------------------------------------

    max_pain = _get_value(data, "max_pain")

    max_pain_strike = 0

    if max_pain is not None:
        if isinstance(max_pain, dict):
            max_pain_strike = max_pain.get("strike", 0)
        else:
            max_pain_strike = getattr(
                max_pain,
                "strike",
                0,
            )

    # ---------------------------------------------------------
    # SUPPORT
    # ---------------------------------------------------------

    support = _get_value(data, "support")

    support_value = 0

    if support is not None:
        if isinstance(support, dict):
            support_value = support.get(
                "support",
                0,
            )
        else:
            support_value = getattr(
                support,
                "support",
                0,
            )

    # ---------------------------------------------------------
    # PCR INTERPRETATION
    # ---------------------------------------------------------

    try:
        pcr_numeric = float(pcr_value)
    except (TypeError, ValueError):
        pcr_numeric = 0

    if pcr_numeric >= 1.20:
        pcr_status = "Strong Bullish"
    elif pcr_numeric >= 1.00:
        pcr_status = "Bullish"
    elif pcr_numeric >= 0.80:
        pcr_status = "Neutral"
    else:
        pcr_status = "Bearish"

    # ---------------------------------------------------------
    # METRIC CARDS
    # ---------------------------------------------------------

    col1, col2, col3, col4 = st.columns(
        4,
        gap="small",
    )

    # ---------------------------------------------------------
    # SPOT
    # ---------------------------------------------------------

    with col1:
        st.metric(
            label="📈 Spot",
            value=_format_number(
                spot_price,
                2,
            ),
            delta="+125.40",
        )

    # ---------------------------------------------------------
    # PCR
    # ---------------------------------------------------------

    with col2:
        st.metric(
            label="🟡 PCR",
            value=_format_number(
                pcr_value,
                2,
            ),
        )

        st.markdown(
            f"""
            <div style="
                color:#00d26a;
                font-weight:600;
                margin-top:-10px;
                font-size:0.82rem;
            ">
                {pcr_status}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # MAX PAIN
    # ---------------------------------------------------------

    with col3:
        st.metric(
            label="🎯 Max Pain",
            value=_format_number(
                max_pain_strike,
                0,
            ),
        )

        st.markdown(
            """
            <div style="
                color:#00d26a;
                font-weight:600;
                margin-top:-10px;
                font-size:0.82rem;
            ">
                Major OI
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------------------------------------------------------
    # SUPPORT
    # ---------------------------------------------------------

    with col4:
        st.metric(
            label="🟢 Support",
            value=_format_number(
                support_value,
                0,
            ),
        )

        st.markdown(
            """
            <div style="
                color:#00d26a;
                font-weight:600;
                margin-top:-10px;
                font-size:0.82rem;
            ">
                Strong
            </div>
            """,
            unsafe_allow_html=True,
        )