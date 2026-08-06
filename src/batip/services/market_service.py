"""
Market Service.
"""

from batip.models import MarketSnapshot
from batip.providers.nse_provider import NSEProvider


class MarketService:

    def __init__(self):
        self.provider = NSEProvider()

    def get_market_snapshot(self) -> MarketSnapshot:

        return MarketSnapshot(
            spot=self.provider.get_spot(),
            future=self.provider.get_future(),
            vix=self.provider.get_vix(),
            status=self.provider.get_market_status(),
            expiry=self.provider.get_expiry(),
        )