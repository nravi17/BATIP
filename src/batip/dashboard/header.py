"""
Professional Dashboard Header
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st


def render_header() -> None:
    """
    Render BATIP professional header.
    """

    st.title("📈 BATIP Pro")

    st.caption(
        "BankNifty Analytics & Trading Intelligence Platform"
    )

    now = datetime.now().strftime("%d-%b-%Y %H:%M:%S")

    st.info(
        f"""
🟢 **MOCK MODE**

**Symbol:** BANKNIFTY &nbsp;&nbsp;|&nbsp;&nbsp;
**Expiry:** 13-Aug-2026 &nbsp;&nbsp;|&nbsp;&nbsp;
**Updated:** {now}
"""
    )

    st.divider()