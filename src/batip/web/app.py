"""
BATIP - Live Trading Dashboard

Phase 2A:
- Live NSE market data
- Option sentiment
- Support / resistance
- OI walls
- Trading signal
- Paper-trading ready
"""

import time
from datetime import datetime

import streamlit as st

from batip.dashboard.service import DashboardService


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="BATIP Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None

if "snapshot" not in st.session_state:
    st.session_state.snapshot = None


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def format_number(value, decimals=2):
    if value is None:
        return "-"

    return f"{value:,.{decimals}f}"


def signal_emoji(signal):
    value = str(signal).upper()

    if "BUY" in value:
        return "🟢"

    if "SELL" in value:
        return "🔴"

    return "🟡"


def load_snapshot(symbol):
    service = DashboardService()
    return service.get_snapshot(symbol)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("⚙️ BATIP")

st.sidebar.markdown(
    "### Market Controls"
)

symbol = st.sidebar.selectbox(
    "Instrument",
    [
        "BANKNIFTY",
        "NIFTY",
    ],
)

refresh_seconds = st.sidebar.selectbox(
    "Refresh Interval",
    [
        10,
        15,
        30,
        60,
    ],
    index=2,
)

manual_refresh = st.sidebar.button(
    "🔄 Refresh Now",
    use_container_width=True,
)


st.sidebar.divider()

st.sidebar.markdown(
    """
### BATIP Status

🟢 NSE Live Data  
🟢 Analytics Engine  
🟢 Signal Engine  
🟡 Paper Trading
"""
)

st.sidebar.caption(
    "Paper trading only. No broker orders are placed."
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("📊 BATIP Trading Dashboard")

st.caption(
    "Banking & Trading Intelligence Platform"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Instrument",
        symbol,
    )

with col2:
    st.metric(
        "Data Source",
        "NSE",
    )

with col3:
    st.metric(
        "Mode",
        "PAPER TRADING",
    )


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

try:

    snapshot = load_snapshot(symbol)

    st.session_state.snapshot = snapshot
    st.session_state.last_refresh = datetime.now()

except Exception as exc:

    st.error(
        f"Unable to retrieve market data: {exc}"
    )

    st.stop()


# ---------------------------------------------------------
# MARKET OVERVIEW
# ---------------------------------------------------------

st.divider()

st.subheader("📈 Market Overview")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric(
        "Spot",
        format_number(snapshot.spot),
    )

with c2:
    st.metric(
        "ATM",
        format_number(snapshot.atm, 0),
    )

with c3:
    st.metric(
        "PCR",
        format_number(snapshot.pcr),
        snapshot.pcr_signal,
    )

with c4:
    st.metric(
        "Max Pain",
        format_number(snapshot.max_pain, 0),
    )

with c5:
    st.metric(
        "Max Pain Distance",
        format_number(snapshot.max_pain_distance),
    )


# ---------------------------------------------------------
# SIGNAL
# ---------------------------------------------------------

st.divider()

st.subheader("🎯 BATIP Trading Signal")

signal_col1, signal_col2, signal_col3, signal_col4 = st.columns(4)

with signal_col1:

    st.metric(
        "Signal",
        f"{signal_emoji(snapshot.signal)} {snapshot.signal}",
    )

with signal_col2:

    st.metric(
        "Direction",
        snapshot.direction,
    )

with signal_col3:

    st.metric(
        "Strength",
        snapshot.strength,
    )

with signal_col4:

    st.metric(
        "Confidence",
        f"{snapshot.confidence:.1f}%",
    )


# ---------------------------------------------------------
# SUPPORT / RESISTANCE
# ---------------------------------------------------------

st.divider()

st.subheader("🧱 Support & Resistance")

sr1, sr2, sr3, sr4 = st.columns(4)

with sr1:
    st.metric(
        "Strong Support",
        format_number(snapshot.strong_support, 0),
    )

with sr2:
    st.metric(
        "Support",
        format_number(snapshot.support, 0),
    )

with sr3:
    st.metric(
        "Resistance",
        format_number(snapshot.resistance, 0),
    )

with sr4:
    st.metric(
        "Strong Resistance",
        format_number(snapshot.strong_resistance, 0),
    )


# ---------------------------------------------------------
# OI WALLS
# ---------------------------------------------------------

st.divider()

st.subheader("🏰 Open Interest Walls")

oi1, oi2, oi3, oi4 = st.columns(4)

with oi1:
    st.metric(
        "Put OI Wall",
        format_number(snapshot.put_oi_wall, 0),
    )

with oi2:
    st.metric(
        "Call OI Wall",
        format_number(snapshot.call_oi_wall, 0),
    )

with oi3:
    st.metric(
        "Max Put ΔOI",
        format_number(snapshot.max_put_delta_oi, 0),
    )

with oi4:
    st.metric(
        "Max Call ΔOI",
        format_number(snapshot.max_call_delta_oi, 0),
    )


# ---------------------------------------------------------
# OI SENTIMENT
# ---------------------------------------------------------

st.divider()

st.subheader("⚖️ OI Sentiment")

oi1, oi2, oi3 = st.columns(3)

with oi1:
    st.metric(
        "Bullish OI",
        snapshot.bullish_oi,
    )

with oi2:
    st.metric(
        "Bearish OI",
        snapshot.bearish_oi,
    )

with oi3:
    st.metric(
        "Neutral OI",
        snapshot.neutral_oi,
    )


score1, score2 = st.columns(2)

with score1:
    st.metric(
        "Signal Score",
        snapshot.score,
    )

with score2:
    st.metric(
        "Confidence",
        f"{snapshot.confidence:.1f}%",
    )


# ---------------------------------------------------------
# DECISION PANEL
# ---------------------------------------------------------

st.divider()

st.subheader("🧠 BATIP Decision Engine")

signal_value = str(snapshot.signal).upper()

if "BUY" in signal_value:

    st.success(
        "🟢 BUY BIAS — BATIP detects a bullish setup."
    )

elif "SELL" in signal_value:

    st.error(
        "🔴 SELL BIAS — BATIP detects a bearish setup."
    )

else:

    st.warning(
        "🟡 WAIT — No strong directional setup."
    )


# ---------------------------------------------------------
# TRADE FRAMEWORK
# ---------------------------------------------------------

st.divider()

st.subheader("💼 Paper Trade Framework")

trade1, trade2, trade3 = st.columns(3)

with trade1:

    st.metric(
        "Entry Reference",
        format_number(snapshot.spot),
    )

with trade2:

    st.metric(
        "Support",
        format_number(snapshot.support, 0),
    )

with trade3:

    st.metric(
        "Resistance",
        format_number(snapshot.resistance, 0),
    )


st.info(
    "This dashboard currently provides market-analysis "
    "levels only. Actual paper-order management will be "
    "added in Phase 2B."
)


# ---------------------------------------------------------
# DATA STATUS
# ---------------------------------------------------------

st.divider()

status1, status2, status3 = st.columns(3)

with status1:

    st.write(
        "**Data Source:** NSE"
    )

with status2:

    st.write(
        "**Status:** 🟢 LIVE"
    )

with status3:

    if st.session_state.last_refresh:

        st.write(
            "**Last Refresh:** "
            + st.session_state.last_refresh.strftime(
                "%H:%M:%S"
            )
        )


# ---------------------------------------------------------
# AUTO REFRESH
# ---------------------------------------------------------

if manual_refresh:

    st.rerun()


time.sleep(refresh_seconds)

st.rerun()