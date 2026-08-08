"""
Support & Resistance Calculator
"""

from dataclasses import dataclass

from batip.models.option_chain import OptionChain


@dataclass(slots=True)
class SupportResistanceResult:
    support: float
    resistance: float
    support_oi: int
    resistance_oi: int


class SupportResistanceCalculator:

    def __init__(self, chain: OptionChain):
        self.chain = chain

    def calculate(self) -> SupportResistanceResult:

        spot = self.chain.spot_price

        # Support must be BELOW spot.
        support_candidates = [
            strike
            for strike in self.chain.strikes
            if strike.strike < spot
        ]

        # Resistance must be ABOVE spot.
        resistance_candidates = [
            strike
            for strike in self.chain.strikes
            if strike.strike > spot
        ]

        # Fallback if the chain doesn't contain strikes on one side.
        if not support_candidates:
            support_candidates = list(self.chain.strikes)

        if not resistance_candidates:
            resistance_candidates = list(self.chain.strikes)

        strongest_support = max(
            support_candidates,
            key=lambda strike: strike.put.open_interest,
        )

        strongest_resistance = max(
            resistance_candidates,
            key=lambda strike: strike.call.open_interest,
        )

        return SupportResistanceResult(
            support=strongest_support.strike,
            resistance=strongest_resistance.strike,
            support_oi=strongest_support.put.open_interest,
            resistance_oi=strongest_resistance.call.open_interest,
        )