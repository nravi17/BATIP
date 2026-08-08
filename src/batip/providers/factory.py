"""
Market Data Provider Factory
"""

from __future__ import annotations

from batip.config import settings
from batip.providers.base_provider import MarketDataProvider
from batip.providers.mock_provider import MockProvider
from batip.providers.nse_provider import NSEProvider


def create_market_data_provider() -> MarketDataProvider:
    """
    Create the configured market-data provider.

    Supported providers:
    - mock
    - nse
    """

    provider = settings.DATA_PROVIDER.lower().strip()

    if provider == "mock":
        return MockProvider()

    if provider == "nse":
        return NSEProvider()

    raise ValueError(
        f"Unsupported DATA_PROVIDER: {settings.DATA_PROVIDER}"
    )