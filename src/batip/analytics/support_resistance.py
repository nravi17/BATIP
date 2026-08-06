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

        strongest_support = max(
            self.chain.strikes,
            key=lambda strike: strike.put.open_interest,
        )

        strongest_resistance = max(
            self.chain.strikes,
            key=lambda strike: strike.call.open_interest,
        )

        return SupportResistanceResult(
            support=strongest_support.strike,
            resistance=strongest_resistance.strike,
            support_oi=strongest_support.put.open_interest,
            resistance_oi=strongest_resistance.call.open_interest,
        )