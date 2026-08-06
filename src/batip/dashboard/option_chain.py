"""
Option Chain Dashboard
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from batip.models import OptionChain


def option_chain_dataframe(chain: OptionChain) -> pd.DataFrame:
    """Convert OptionChain into a DataFrame."""

    rows = []

    for strike in chain.strikes:
        rows.append(
            {
                "Call OI": strike.call.open_interest,
                "Call Chg OI": strike.call.change_in_oi,
                "Call IV": strike.call.implied_volatility,
                "Call LTP": strike.call.last_price,
                "Strike": strike.strike,
                "Put LTP": strike.put.last_price,
                "Put IV": strike.put.implied_volatility,
                "Put Chg OI": strike.put.change_in_oi,
                "Put OI": strike.put.open_interest,
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