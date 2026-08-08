"""
BATIP Market Bias Engine
Converts option-chain analytics into a deterministic
market-bias assessment.
This is intentionally rule-based.
No AI/LLM dependency is used here.
"""
from dataclasses import dataclass
from enum import Enum

from batip.models.option_chain import OptionChain


class MarketBias(str, Enum):
    STRONG_BULLISH = "Strong Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    STRONG_BEARISH = "Strong Bearish"


@dataclass(slots=True)
class MarketBiasResult:
    bias: MarketBias
    score: int
    confidence: float
    reason: str


class MarketBiasEngine:
    """
    Determine market bias from current option-chain structure.
    """

    def __init__(
        self,
        chain: OptionChain,
        pcr: float,
    ) -> None:
        self.chain = chain
        self.pcr = pcr

    def _calculate_oi_totals(self) -> tuple[int, int]:
        call_oi = 0
        put_oi = 0

        for strike in self.chain.strikes:
            call_oi += strike.call.open_interest
            put_oi += strike.put.open_interest

        return call_oi, put_oi

    def _calculate_change_totals(self) -> tuple[int, int]:
        call_change = 0
        put_change = 0

        for strike in self.chain.strikes:
            call_change += strike.call.change_in_oi
            put_change += strike.put.change_in_oi

        return call_change, put_change

    def calculate(self) -> MarketBiasResult:
        score = 0
        reasons = []

        call_oi, put_oi = self._calculate_oi_totals()
        call_change, put_change = self._calculate_change_totals()

        # --------------------------------------------------
        # OI PCR
        # --------------------------------------------------

        if self.pcr >= 1.20:
            score += 2
            reasons.append("strong Put OI dominance")
        elif self.pcr >= 1.00:
            score += 1
            reasons.append("Put OI slightly dominates")
        elif self.pcr <= 0.80:
            score -= 2
            reasons.append("strong Call OI dominance")
        elif self.pcr >= 0.85:
            # 0.85 - 0.99 = neutral / balanced zone
            reasons.append("PCR is within the neutral range")
        else:
            score -= 1
            reasons.append("Call OI slightly dominates")

        # --------------------------------------------------
        # Change OI
        # --------------------------------------------------

        if put_change > call_change:
            score += 1
            reasons.append(
                "Put OI addition exceeds Call OI addition"
            )
        elif call_change > put_change:
            score -= 1
            reasons.append(
                "Call OI addition exceeds Put OI addition"
            )
        else:
            reasons.append(
                "Call and Put OI additions are balanced"
            )

        # --------------------------------------------------
        # Determine bias
        # --------------------------------------------------

        if score >= 3:
            bias = MarketBias.STRONG_BULLISH
        elif score >= 1:
            bias = MarketBias.BULLISH
        elif score <= -3:
            bias = MarketBias.STRONG_BEARISH
        elif score <= -1:
            bias = MarketBias.BEARISH
        else:
            bias = MarketBias.NEUTRAL

        confidence = min(
            95.0,
            50.0 + abs(score) * 12.5,
        )

        reason = "; ".join(reasons)

        if not reason:
            reason = "OI structure is relatively balanced"

        return MarketBiasResult(
            bias=bias,
            score=score,
            confidence=confidence,
            reason=reason,
        )