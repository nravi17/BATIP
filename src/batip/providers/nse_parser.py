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
    """
    Converts NSE JSON payloads into BATIP domain models.
    """

    def _parse_leg(
        self,
        strike: float,
        option_type: str,
        data: dict,
    ) -> OptionLeg:
        """
        Convert one NSE CE/PE record into an OptionLeg.
        """
        return OptionLeg(
            strike=float(strike),
            option_type=option_type,
            last_price=float(
                data.get("lastPrice", 0.0) or 0.0
            ),
            bid_price=float(
                data.get("bidprice", 0.0) or 0.0
            ),
            ask_price=float(
                data.get("askPrice", 0.0) or 0.0
            ),
            volume=int(
                data.get("totalTradedVolume", 0) or 0
            ),
            open_interest=int(
                data.get("openInterest", 0) or 0
            ),
            change_in_oi=int(
                data.get("changeinOpenInterest", 0) or 0
            ),
            implied_volatility=float(
                data.get("impliedVolatility", 0.0) or 0.0
            ),
            previous_close=float(
                data.get("prevClose", 0.0) or 0.0
            ),
            price_change=float(
                data.get("change", 0.0) or 0.0
            ),
            price_change_percent=float(
                data.get("pChange", 0.0) or 0.0
            ),
        )

    def parse_option_chain(
        self,
        payload: dict,
    ) -> OptionChain:
        """
        Parse the NSE option-chain response.
        """
        if not isinstance(payload, dict):
            raise ValueError(
                "NSE payload must be a dictionary"
            )

        records = payload.get("records")

        if not isinstance(records, dict):
            raise ValueError(
                "Invalid NSE response: missing records"
            )

        symbol = records.get(
            "underlying",
            "BANKNIFTY",
        )

        expiry_dates = records.get(
            "expiryDates",
            [],
        )

        expiry = (
            expiry_dates[0]
            if expiry_dates
            else ""
        )

        spot_price = float(
            records.get(
                "underlyingValue",
                0.0,
            )
            or 0.0
        )

        chain = OptionChain(
            symbol=symbol,
            expiry=expiry,
            spot_price=spot_price,
            timestamp=datetime.now(),
        )

        for item in records.get("data", []):
            if not isinstance(item, dict):
                continue

            strike_value = item.get(
                "strikePrice"
            )

            if strike_value is None:
                continue

            try:
                strike = float(strike_value)
            except (
                TypeError,
                ValueError,
            ):
                continue

            call_data = item.get("CE")
            put_data = item.get("PE")

            # BATIP currently expects both legs.
            if not isinstance(call_data, dict):
                continue

            if not isinstance(put_data, dict):
                continue

            call = self._parse_leg(
                strike=strike,
                option_type="CE",
                data=call_data,
            )

            put = self._parse_leg(
                strike=strike,
                option_type="PE",
                data=put_data,
            )

            chain.strikes.append(
                OptionStrike(
                    strike=strike,
                    call=call,
                    put=put,
                )
            )

        if not chain.strikes:
            raise ValueError(
                "NSE response contained no valid option strikes"
            )

        return chain