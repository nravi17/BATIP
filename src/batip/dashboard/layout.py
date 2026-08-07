"""
Dashboard Layout
"""

from __future__ import annotations

from batip.dashboard.header import render_header
from batip.dashboard.metrics import render_metrics
from batip.dashboard.footer import render_footer
from batip.dashboard.option_chain import render_option_chain
from batip.dashboard.oi_intelligence import render_oi_intelligence


def _get_value(data, key, default=None):
    """
    Read a value from either a dictionary or an object.

    This keeps the dashboard compatible with the current
    MarketService dictionary response and future view models.
    """

    if isinstance(data, dict):
        return data.get(key, default)

    return getattr(data, key, default)


def render_dashboard(data) -> None:
    """
    Render the complete BATIP dashboard.
    """

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    render_header()

    # ---------------------------------------------------------
    # EXTRACT DASHBOARD DATA
    # ---------------------------------------------------------

    chain = _get_value(data, "chain")

    # ---------------------------------------------------------
    # TOP METRICS
    # ---------------------------------------------------------

    render_metrics(data)

    # ---------------------------------------------------------
    # OPTION CHAIN
    # ---------------------------------------------------------

    if chain is not None:
        render_option_chain(chain)

    # ---------------------------------------------------------
    # OI INTELLIGENCE
    # ---------------------------------------------------------

    render_oi_intelligence(data)

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------

    render_footer()