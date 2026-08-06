"""
BATIP Max Pain Calculator
"""

from dataclasses import dataclass

from batip.models import OptionChain


@dataclass(slots=True)
class MaxPainResult:
    strike: float
    total_pain: float


class MaxPainCalculator:

    def __init__(self, chain: OptionChain):
        self.chain = chain

    def calculate(self) -> MaxPainResult:

        min_pain = float("inf")
        max_pain_strike = 0.0

        strikes = self.chain.strikes

        for expiry_price in strikes:

            pain = 0.0

            for option in strikes:

                # Call Pain
                if expiry_price.strike > option.strike:
                    pain += (
                        expiry_price.strike - option.strike
                    ) * option.call.open_interest

                # Put Pain
                if expiry_price.strike < option.strike:
                    pain += (
                        option.strike - expiry_price.strike
                    ) * option.put.open_interest

            if pain < min_pain:
                min_pain = pain
                max_pain_strike = expiry_price.strike

        return MaxPainResult(
            strike=max_pain_strike,
            total_pain=min_pain,
        )