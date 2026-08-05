from datetime import datetime

from batip.models import (
    ExpiryInfo,
    FutureQuote,
    MarketStatus,
    SpotQuote,
    VixQuote,
)
from batip.providers.base import MarketDataProvider


class NSEProvider(MarketDataProvider):

    def get_spot(self):

        return SpotQuote(
            symbol="BANKNIFTY",
            price=58145.25,
            change=125.40,
            change_percent=0.22,
            timestamp=datetime.now(),
        )

    def get_future(self):

        return FutureQuote(
            symbol="BANKNIFTY",
            expiry="Current Week",
            price=58192.50,
            change=132.70,
            change_percent=0.23,
            open_interest=None,
            timestamp=datetime.now(),
        )

    def get_vix(self):

        return VixQuote(
            value=12.84,
            change=-0.35,
            change_percent=-2.65,
            timestamp=datetime.now(),
        )

    def get_market_status(self):

        return MarketStatus(
            is_open=True,
            message="Market Open",
            timestamp=datetime.now(),
        )

    def get_expiry(self):

        return ExpiryInfo(
            current_week="06-Aug-2026",
            next_week="13-Aug-2026",
            monthly="27-Aug-2026",
        )