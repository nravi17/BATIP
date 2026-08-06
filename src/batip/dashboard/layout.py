"""
Dashboard Layout
"""

from __future__ import annotations

from batip.dashboard.footer import render_footer
from batip.dashboard.header import render_header
from batip.dashboard.metrics import render_metrics
from batip.dashboard.option_chain import render_option_chain


def render_dashboard(data: dict) -> None:
    """Render complete dashboard."""

    render_header()

    render_metrics(data)

    render_option_chain(data["chain"])

    render_footer()