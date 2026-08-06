"""
Dashboard ViewModel
"""

from dataclasses import dataclass


@dataclass(slots=True)
class DashboardViewModel:
    """Display-ready data for the dashboard."""

    symbol: str
    expiry: str
    spot: str

    pcr: str

    max_pain: str

    support: str

    resistance: str

    market_status: str = "🟢 MOCK"

    updated: str = ""