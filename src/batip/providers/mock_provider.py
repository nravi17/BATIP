"""
Mock Provider
"""

from datetime import datetime

from batip.models import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)
from batip.providers.base_provider import MarketDataProvider


class MockProvider(MarketDataProvider):
    """Mock provider for dashboard development."""

    def get_option_chain(
        self,
        symbol: str = "BANKNIFTY",
    ) -> OptionChain:

        chain = OptionChain(
            symbol=symbol,
            expiry="13-Aug-2026",
            spot_price=58145.25,
            timestamp=datetime.now(),
        )

        for strike in range(57100, 59200, 100):

            call = OptionLeg(
                strike=strike,
                option_type="CE",
                last_price=max(10, 300 - abs(58100 - strike) / 2),
                bid_price=100,
                ask_price=101,
                volume=10000,
                open_interest=400000 + (58100 - strike) * 10,
                change_in_oi=5000,
                implied_volatility=14.5,
            )

            put = OptionLeg(
                strike=strike,
                option_type="PE",
                last_price=max(10, 300 - abs(strike - 58100) / 2),
                bid_price=99,
                ask_price=100,
                volume=9000,
                open_interest=420000 + (strike - 58100) * 10,
                change_in_oi=4500,
                implied_volatility=15.0,
            )

            chain.strikes.append(
                OptionStrike(
                    strike=strike,
                    call=call,
                    put=put,
                )
            )

        return chain