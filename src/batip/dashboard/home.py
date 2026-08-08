"""
Dashboard Home
"""

from batip.dashboard.layout import render_dashboard
from batip.dashboard.styles import load_styles
from batip.providers.factory import create_market_data_provider
from batip.services.market_service import MarketService


def run_dashboard() -> None:
    """
    BATIP Dashboard Entry Point.
    """

    load_styles()

    provider = create_market_data_provider()

    service = MarketService(provider)

    dashboard_data = service.get_dashboard_data()

    render_dashboard(dashboard_data)