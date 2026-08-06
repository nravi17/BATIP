"""
Put Call Ratio (PCR) Calculator.
"""

from batip.analytics.models import AnalyticsResult
from batip.models import OptionChain


class PCRCalculator:

    def __init__(self, chain: OptionChain):
        self.chain = chain

    def calculate(self) -> AnalyticsResult:

        total_call_oi = sum(
            strike.call.open_interest
            for strike in self.chain.strikes
        )

        total_put_oi = sum(
            strike.put.open_interest
            for strike in self.chain.strikes
        )

        if total_call_oi == 0:
            value = 0.0
        else:
            value = total_put_oi / total_call_oi

        signal, description = self._classify(value)

        return AnalyticsResult(
            name="PCR",
            value=round(value, 2),
            signal=signal,
            description=description,
        )

    @staticmethod
    def _classify(value: float):

        if value < 0.70:
            return (
                "Bearish",
                "More Call writing than Put writing.",
            )

        if value < 1.00:
            return (
                "Neutral",
                "Balanced market sentiment.",
            )

        if value < 1.30:
            return (
                "Bullish",
                "Healthy Put writing observed.",
            )

        return (
            "Extreme Bullish",
            "High PCR may indicate possible reversal if overextended.",
        )