"""
Professional Option Chain Dashboard
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from batip.models import OptionChain


def option_chain_dataframe(chain: OptionChain) -> pd.DataFrame:
    """Convert OptionChain into a dashboard-friendly DataFrame."""

    rows: list[dict] = []

    spot = chain.spot_price

    for strike in chain.strikes:

        if abs(strike.strike - spot) < 50:
            strike_type = "🟡 ATM"
        elif strike.strike < spot:
            strike_type = "🟢 ITM"
        else:
            strike_type = "⚪ OTM"

        rows.append(
            {
                "Call OI": strike.call.open_interest,
                "Call Chg OI": strike.call.change_in_oi,
                "Call IV": strike.call.implied_volatility,
                "Call LTP": strike.call.last_price,
                "Strike": strike.strike,
                "Type": strike_type,
                "Put LTP": strike.put.last_price,
                "Put IV": strike.put.implied_volatility,
                "Put Chg OI": strike.put.change_in_oi,
                "Put OI": strike.put.open_interest,
            }
        )

    return pd.DataFrame(rows)


def _format_oi(value: float | int) -> str:
    """Format open interest for display."""

    return f"{value:,.0f}"


def _format_price(value: float | int) -> str:
    """Format option price."""

    return f"{value:,.2f}"


def _format_iv(value: float | int) -> str:
    """Format implied volatility."""

    return f"{value:.2f}%"


def _format_change(value: float | int) -> str:
    """Format change in open interest."""

    return f"{value:+,.0f}"


def _style_option_chain(
    dataframe: pd.DataFrame,
    spot: float,
) -> pd.io.formats.style.Styler:
    """Apply professional styling to the option-chain table."""

    def highlight_strike(row: pd.Series) -> list[str]:
        styles = [""] * len(row)

        strike_position = row.index.get_loc("Strike")

        if abs(float(row["Strike"]) - spot) < 50:
            styles[strike_position] = (
                "font-weight: bold; "
                "background-color: rgba(255, 193, 7, 0.18);"
            )

        return styles

    def highlight_type(value: str) -> str:
        if "ATM" in value:
            return (
                "font-weight: bold; "
                "background-color: rgba(255, 193, 7, 0.18);"
            )

        if "ITM" in value:
            return (
                "font-weight: bold; "
                "background-color: rgba(76, 175, 80, 0.12);"
            )

        return (
            "font-weight: bold; "
            "background-color: rgba(158, 158, 158, 0.10);"
        )

    styled = dataframe.style

    styled = styled.apply(highlight_strike, axis=1)

    styled = styled.map(
        highlight_type,
        subset=["Type"],
    )

    return styled


def render_option_chain(chain: OptionChain) -> None:
    """Render the professional option-chain table."""

    st.subheader("📊 Option Chain")

    dataframe = option_chain_dataframe(chain)

    if dataframe.empty:
        st.info("No option-chain data available.")
        return

    display_dataframe = dataframe.copy()

    display_dataframe["Call OI"] = display_dataframe["Call OI"].map(
        _format_oi
    )

    display_dataframe["Call Chg OI"] = display_dataframe[
        "Call Chg OI"
    ].map(_format_change)

    display_dataframe["Call IV"] = display_dataframe["Call IV"].map(
        _format_iv
    )

    display_dataframe["Call LTP"] = display_dataframe["Call LTP"].map(
        _format_price
    )

    display_dataframe["Put LTP"] = display_dataframe["Put LTP"].map(
        _format_price
    )

    display_dataframe["Put IV"] = display_dataframe["Put IV"].map(
        _format_iv
    )

    display_dataframe["Put Chg OI"] = display_dataframe[
        "Put Chg OI"
    ].map(_format_change)

    display_dataframe["Put OI"] = display_dataframe["Put OI"].map(
        _format_oi
    )

    styled = _style_option_chain(
        display_dataframe,
        chain.spot_price,
    )

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Spot: {chain.spot_price:,.2f}  •  "
        f"Expiry: {chain.expiry}"
    )