"""
OI Intelligence Dashboard Component
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


def _get_leg_value(leg, key, default=0):
    """
    Read option-leg data from either dictionary or object.
    """

    if leg is None:
        return default

    if isinstance(leg, dict):
        return leg.get(key, default)

    return getattr(leg, key, default)


def _get_strike_value(strike_data, key, default=None):
    """
    Read strike-level data from either dictionary or object.
    """

    if isinstance(strike_data, dict):
        return strike_data.get(key, default)

    return getattr(
        strike_data,
        key,
        default,
    )


def _number(value, default=0):
    """
    Safely convert a value to float.
    """

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def render_oi_intelligence(data) -> None:
    """
    Render Open Interest intelligence.
    """

    # ---------------------------------------------------------
    # GET OPTION CHAIN
    # ---------------------------------------------------------

    chain = _get_value(
        data,
        "chain",
    )

    if chain is None:

        st.warning(
            "Option chain data is not available."
        )

        return

    strikes = _get_value(
        chain,
        "strikes",
        [],
    )

    if not strikes:

        st.warning(
            "No option chain data available for OI analysis."
        )

        return

    # ---------------------------------------------------------
    # INITIAL VALUES
    # ---------------------------------------------------------

    total_call_oi = 0
    total_put_oi = 0

    total_call_change = 0
    total_put_change = 0

    max_call_oi = None
    max_put_oi = None

    max_call_change = None
    max_put_change = None

    # ---------------------------------------------------------
    # PROCESS OPTION CHAIN
    # ---------------------------------------------------------

    for strike_data in strikes:

        strike = _get_strike_value(
            strike_data,
            "strike",
            0,
        )

        call = _get_strike_value(
            strike_data,
            "call",
        )

        put = _get_strike_value(
            strike_data,
            "put",
        )

        # -----------------------------------------------------
        # CALL
        # -----------------------------------------------------

        if call is not None:

            call_oi = _number(
                _get_leg_value(
                    call,
                    "open_interest",
                    0,
                )
            )

            call_change = _number(
                _get_leg_value(
                    call,
                    "change_in_oi",
                    0,
                )
            )

            total_call_oi += call_oi

            total_call_change += call_change

            if (
                max_call_oi is None
                or call_oi > max_call_oi[1]
            ):

                max_call_oi = (
                    strike,
                    call_oi,
                )

            if (
                max_call_change is None
                or call_change > max_call_change[1]
            ):

                max_call_change = (
                    strike,
                    call_change,
                )

        # -----------------------------------------------------
        # PUT
        # -----------------------------------------------------

        if put is not None:

            put_oi = _number(
                _get_leg_value(
                    put,
                    "open_interest",
                    0,
                )
            )

            put_change = _number(
                _get_leg_value(
                    put,
                    "change_in_oi",
                    0,
                )
            )

            total_put_oi += put_oi

            total_put_change += put_change

            if (
                max_put_oi is None
                or put_oi > max_put_oi[1]
            ):

                max_put_oi = (
                    strike,
                    put_oi,
                )

            if (
                max_put_change is None
                or put_change > max_put_change[1]
            ):

                max_put_change = (
                    strike,
                    put_change,
                )

    # ---------------------------------------------------------
    # PCR
    # ---------------------------------------------------------

    if total_call_oi > 0:

        oi_pcr = (
            total_put_oi /
            total_call_oi
        )

    else:

        oi_pcr = 0

    if total_call_change > 0:

        change_pcr = (
            total_put_change /
            total_call_change
        )

    else:

        change_pcr = 0

    # ---------------------------------------------------------
    # SECTION HEADER
    # ---------------------------------------------------------

    st.markdown(
        '<div style="margin-top:35px; margin-bottom:15px;">'
        '<h2 style="font-size:28px; margin-bottom:4px;">🧠 OI Intelligence</h2>'
        '<p style="color:#9aa4b2; font-size:14px;">'
        'Open Interest structure and market positioning'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Call OI",
            f"{total_call_oi:,.0f}",
        )

    with col2:

        st.metric(
            "Put OI",
            f"{total_put_oi:,.0f}",
        )

    with col3:

        st.metric(
            "OI PCR",
            f"{oi_pcr:.2f}",
        )

    with col4:

        st.metric(
            "Change OI PCR",
            f"{change_pcr:.2f}",
        )

    # ---------------------------------------------------------
    # POSITIONING
    # ---------------------------------------------------------

    st.markdown(
        "### 📊 OI Positioning"
    )

    col1, col2 = st.columns(2)

    # ---------------------------------------------------------
    # CALL
    # ---------------------------------------------------------

    with col1:

        st.markdown(
            "#### 🔴 Call Side"
        )

        if max_call_oi:

            st.write(
                f"**Highest Call OI:** "
                f"{max_call_oi[0]:,.0f} "
                f"→ "
                f"{max_call_oi[1]:,.0f}"
            )

        if max_call_change:

            st.write(
                f"**Highest Call Chg OI:** "
                f"{max_call_change[0]:,.0f} "
                f"→ +"
                f"{max_call_change[1]:,.0f}"
            )

        st.write(
            f"**Total Call Chg OI:** "
            f"+{total_call_change:,.0f}"
        )

    # ---------------------------------------------------------
    # PUT
    # ---------------------------------------------------------

    with col2:

        st.markdown(
            "#### 🟢 Put Side"
        )

        if max_put_oi:

            st.write(
                f"**Highest Put OI:** "
                f"{max_put_oi[0]:,.0f} "
                f"→ "
                f"{max_put_oi[1]:,.0f}"
            )

        if max_put_change:

            st.write(
                f"**Highest Put Chg OI:** "
                f"{max_put_change[0]:,.0f} "
                f"→ +"
                f"{max_put_change[1]:,.0f}"
            )

        st.write(
            f"**Total Put Chg OI:** "
            f"+{total_put_change:,.0f}"
        )

    # ---------------------------------------------------------
    # MARKET INTERPRETATION
    # ---------------------------------------------------------

    st.markdown(
        "### 🎯 Market Interpretation"
    )

    if oi_pcr >= 1.20:

        st.success(
            "Bullish OI structure — Put OI is "
            "significantly higher than Call OI."
        )

    elif oi_pcr >= 1.00:

        st.info(
            "Moderately bullish OI structure — "
            "Put OI is slightly higher than Call OI."
        )

    elif oi_pcr >= 0.80:

        st.warning(
            "Neutral OI structure — Call and Put OI "
            "are relatively balanced."
        )

    else:

        st.error(
            "Bearish OI structure — Call OI is "
            "significantly higher than Put OI."
        )

    # ---------------------------------------------------------
    # MAJOR OI LEVELS
    # ---------------------------------------------------------

    st.markdown(
        "### 🛡️ Major OI Levels"
    )

    col1, col2 = st.columns(2)

    with col1:

        if max_put_oi:

            st.success(
                f"Potential Support: "
                f"{max_put_oi[0]:,.0f}\n\n"
                f"Put OI: "
                f"{max_put_oi[1]:,.0f}"
            )

    with col2:

        if max_call_oi:

            st.error(
                f"Potential Resistance: "
                f"{max_call_oi[0]:,.0f}\n\n"
                f"Call OI: "
                f"{max_call_oi[1]:,.0f}"
            )

    st.divider()