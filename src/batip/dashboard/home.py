"""
Dashboard Home
"""

from batip.dashboard.layout import render_dashboard
from batip.dashboard.styles import load_styles
from batip.providers.mock_provider import MockProvider
from batip.services.market_service import MarketService


def run_dashboard() -> None:
    """
    BATIP Dashboard Entry Point.
    """

    load_styles()

    provider = MockProvider()

    service = MarketService(provider)

    dashboard_data = service.get_dashboard_data()

    render_dashboard(dashboard_data)