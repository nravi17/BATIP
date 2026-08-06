"""
Option Chain Dashboard
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from batip.models import OptionChain


def option_chain_dataframe(chain: OptionChain) -> pd.DataFrame:
    """Convert OptionChain into a formatted DataFrame."""

    rows = []

    spot = chain.spot_price

    for strike in chain.strikes:

        if abs(strike.strike - spot) < 50:
            strike_type = "🟡 ATM"
        elif strike.strike < spot:
            strike_type = "ITM"
        else:
            strike_type = "OTM"

        rows.append(
            {
                "Call OI": f"{strike.call.open_interest:,}",
                "Call Chg OI": f"{strike.call.change_in_oi:,}",
                "Call IV": f"{strike.call.implied_volatility:.2f}",
                "Call LTP": f"{strike.call.last_price:.2f}",
                "Strike": strike.strike,
                "Type": strike_type,
                "Put LTP": f"{strike.put.last_price:.2f}",
                "Put IV": f"{strike.put.implied_volatility:.2f}",
                "Put Chg OI": f"{strike.put.change_in_oi:,}",
                "Put OI": f"{strike.put.open_interest:,}",
            }
        )

    return pd.DataFrame(rows)


def render_option_chain(chain: OptionChain) -> None:
    """Render the option chain."""

    st.subheader("📊 Live Option Chain")

    df = option_chain_dataframe(chain)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )