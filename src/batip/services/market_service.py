"""
Market Service.
"""

from batip.models import MarketSnapshot
from batip.providers.nse_provider import NSEProvider
from batip.providers.base_provider import MarketDataProvider


class MarketService:

    def __init__(
        self,
        provider: MarketDataProvider,
    ):
        self.provider = provider