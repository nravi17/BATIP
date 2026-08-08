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
        """
        Return a mock option chain for UI development.
        """
        chain = OptionChain(
            symbol=symbol,
            expiry="13-Aug-2026",
            spot_price=58145.25,
            timestamp=datetime.now(),
        )

        for strike in range(57100, 59200, 100):
            # Mock option premium
            call_price = max(
                5.0,
                450 - abs(strike - 58100) * 2,
            )
            put_price = max(
                5.0,
                450 - abs(58100 - strike) * 2,
            )

            call = OptionLeg(
                strike=strike,
                option_type="CE",
                last_price=call_price,
                bid_price=max(call_price - 1, 1),
                ask_price=call_price + 1,
                volume=10000 + (59100 - strike),
                open_interest=400000 + (58100 - strike) * 10,
                change_in_oi=5000,
                implied_volatility=14.5,
            )

            put = OptionLeg(
                strike=strike,
                option_type="PE",
                last_price=put_price,
                bid_price=max(put_price - 1, 1),
                ask_price=put_price + 1,
                volume=9000 + (strike - 57100),
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

        chain.source = "MOCK"
        chain.data_status = "MOCK"

        return chain