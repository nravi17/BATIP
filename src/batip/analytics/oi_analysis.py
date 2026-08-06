from dataclasses import dataclass
from enum import Enum
from batip.models.option_chain import OptionChain


class OIType(str, Enum):
    LONG_BUILDUP = "Long Build-up"
    SHORT_BUILDUP = "Short Build-up"
    SHORT_COVERING = "Short Covering"
    LONG_UNWINDING = "Long Unwinding"
    NEUTRAL = "Neutral"


@dataclass(slots=True)
class OIAnalysis:

    strike: float

    option_type: str

    price_change: float

    oi_change: int

    signal: OIType

class OIAnalyzer:
    """
    Analyze Open Interest (OI) build-up patterns.
    """

    def __init__(self, chain: OptionChain):
        self.chain = chain

    @staticmethod
    def classify(price_change: float, oi_change: int) -> OIType:

        if price_change > 0 and oi_change > 0:
            return OIType.LONG_BUILDUP

        if price_change < 0 and oi_change > 0:
            return OIType.SHORT_BUILDUP

        if price_change > 0 and oi_change < 0:
            return OIType.SHORT_COVERING

        if price_change < 0 and oi_change < 0:
            return OIType.LONG_UNWINDING

        return OIType.NEUTRAL

    def analyze(self) -> list[OIAnalysis]:

        results = []

        for strike in self.chain.strikes:

            # Temporary approximation until we add previous_close
            call_price_change = (
                strike.call.last_price - strike.call.bid_price
            )

            put_price_change = (
                strike.put.last_price - strike.put.bid_price
            )

            results.append(
                OIAnalysis(
                    strike=strike.strike,
                    option_type="CE",
                    price_change=call_price_change,
                    oi_change=strike.call.change_in_oi,
                    signal=self.classify(
                        call_price_change,
                        strike.call.change_in_oi,
                    ),
                )
            )

            results.append(
                OIAnalysis(
                    strike=strike.strike,
                    option_type="PE",
                    price_change=put_price_change,
                    oi_change=strike.put.change_in_oi,
                    signal=self.classify(
                        put_price_change,
                        strike.put.change_in_oi,
                    ),
                )
            )

        return results