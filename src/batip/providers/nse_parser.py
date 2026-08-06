"""
NSE Option Chain Parser
"""

from __future__ import annotations

from datetime import datetime

from batip.models import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)


class NSEParser:
    """Converts NSE JSON into BATIP domain models."""

    def _parse_leg(
        self,
        strike: float,
        option_type: str,
        data: dict,
    ) -> OptionLeg:

        return OptionLeg(
            strike=strike,
            option_type=option_type,
            last_price=data.get("lastPrice", 0.0),
            bid_price=data.get("bidprice", 0.0),
            ask_price=data.get("askPrice", 0.0),
            volume=data.get("totalTradedVolume", 0),
            open_interest=data.get("openInterest", 0),
            change_in_oi=data.get("changeinOpenInterest", 0),
            implied_volatility=data.get("impliedVolatility", 0.0),
        )

    def parse_option_chain(
        self,
        payload: dict,
    ) -> OptionChain:

        records = payload["records"]

        chain = OptionChain(
            symbol=records.get("underlying", "BANKNIFTY"),
            expiry=records["expiryDates"][0],
            spot_price=records.get("underlyingValue", 0.0),
            timestamp=datetime.now(),
        )

        for item in records["data"]:

            if "CE" not in item or "PE" not in item:
                continue

            strike = item["strikePrice"]

            call = self._parse_leg(
                strike,
                "CE",
                item["CE"],
            )

            put = self._parse_leg(
                strike,
                "PE",
                item["PE"],
            )

            chain.strikes.append(
                OptionStrike(
                    strike=strike,
                    call=call,
                    put=put,
                )
            )

        return chain