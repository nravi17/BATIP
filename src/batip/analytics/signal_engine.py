"""
BATIP Signal Engine

Combines existing BATIP analytics into one deterministic,
explainable market signal.

No AI/LLM dependency is used.
"""

from batip.analytics.market_bias import MarketBias, MarketBiasEngine
from batip.analytics.signal import (
    Signal,
    SignalResult,
    SignalStrength,
)


class SignalEngine:
    """
    Convert existing market analytics into a single signal.
    """

    def __init__(
        self,
        chain,
        pcr: float,
        max_pain,
        support_resistance,
    ) -> None:
        self.chain = chain
        self.pcr = pcr
        self.max_pain = max_pain
        self.support_resistance = support_resistance

    def _market_bias_score(self) -> tuple[int, list[str]]:
        result = MarketBiasEngine(
            self.chain,
            pcr=self.pcr,
        ).calculate()

        if result.bias == MarketBias.STRONG_BULLISH:
            return 2, ["Market bias is strongly bullish"]

        if result.bias == MarketBias.BULLISH:
            return 1, ["Market bias is bullish"]

        if result.bias == MarketBias.STRONG_BEARISH:
            return -2, ["Market bias is strongly bearish"]

        if result.bias == MarketBias.BEARISH:
            return -1, ["Market bias is bearish"]

        return 0, ["Market bias is neutral"]

    def _pcr_score(self) -> tuple[int, list[str]]:
        if self.pcr >= 1.20:
            return 2, ["PCR indicates strong bullish positioning"]

        if self.pcr >= 1.00:
            return 1, ["PCR indicates mild bullish positioning"]

        if self.pcr <= 0.80:
            return -2, ["PCR indicates strong bearish positioning"]

        if self.pcr < 0.85:
            return -1, ["PCR indicates mild bearish positioning"]

        return 0, ["PCR is within the neutral range"]

    def _oi_change_score(self) -> tuple[int, list[str]]:
        call_change = 0
        put_change = 0

        for strike in self.chain.strikes:
            call_change += strike.call.change_in_oi
            put_change += strike.put.change_in_oi

        if put_change > call_change:
            return 2, ["Put OI addition exceeds Call OI addition"]

        if call_change > put_change:
            return -2, ["Call OI addition exceeds Put OI addition"]

        return 0, ["Call and Put OI additions are balanced"]

    def _support_resistance_score(self) -> tuple[int, list[str]]:
        spot = self.chain.spot_price
        support = self.support_resistance.support
        resistance = self.support_resistance.resistance

        if spot > resistance:
            return 2, ["Spot is above calculated resistance"]

        if spot < support:
            return -2, ["Spot is below calculated support"]

        return 0, ["Spot is trading within support and resistance"]

    def _max_pain_score(self) -> tuple[int, list[str]]:
        spot = self.chain.spot_price
        max_pain = self.max_pain.strike

        difference = spot - max_pain

        if difference > 0:
            return 1, ["Spot is above Max Pain"]

        if difference < 0:
            return -1, ["Spot is below Max Pain"]

        return 0, ["Spot is at Max Pain"]

    def component_scores(self) -> dict[str, int]:
        """Return the individual signal component scores."""

        scores: dict[str, int] = {}

        market_score, _ = self._market_bias_score()
        pcr_score, _ = self._pcr_score()
        oi_score, _ = self._oi_change_score()
        sr_score, _ = self._support_resistance_score()
        max_pain_score, _ = self._max_pain_score()

        scores["market_bias"] = market_score
        scores["pcr"] = pcr_score
        scores["oi_change"] = oi_score
        scores["support_resistance"] = sr_score
        scores["max_pain"] = max_pain_score

        return scores

    def calculate(self) -> SignalResult:
        score = 0
        reasons: list[str] = []

        scorers = (
            self._market_bias_score,
            self._pcr_score,
            self._oi_change_score,
            self._support_resistance_score,
            self._max_pain_score,
        )

        for scorer in scorers:
            component_score, component_reasons = scorer()

            score += component_score
            reasons.extend(component_reasons)

        # --------------------------------------------------
        # Final signal
        # --------------------------------------------------

        if score >= 7:
            signal = Signal.STRONG_BUY
            strength = SignalStrength.STRONG
            direction = "Bullish"

        elif score >= 4:
            signal = Signal.BUY
            strength = SignalStrength.MODERATE
            direction = "Bullish"

        elif score <= -7:
            signal = Signal.STRONG_SELL
            strength = SignalStrength.STRONG
            direction = "Bearish"

        elif score <= -4:
            signal = Signal.SELL
            strength = SignalStrength.MODERATE
            direction = "Bearish"

        else:
            signal = Signal.WAIT
            strength = SignalStrength.WEAK
            direction = "Neutral"

        confidence = min(
            95.0,
            50.0 + abs(score) * 5.0,
        )

        return SignalResult(
            signal=signal,
            strength=strength,
            score=score,
            confidence=confidence,
            direction=direction,
            reasons=reasons,
        )