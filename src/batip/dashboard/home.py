"""
Dashboard Home
"""

from batip.dashboard.layout import render_dashboard
from batip.providers.mock_provider import MockProvider
from batip.services.market_service import MarketService


def run_dashboard():

    provider = MockProvider()

    service = MarketService(provider)

    dashboard_data = service.get_dashboard_data()

    render_dashboard(dashboard_data)