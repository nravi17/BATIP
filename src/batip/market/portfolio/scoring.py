"""
BATIP Portfolio Scoring Engine.

Converts stock-level intelligence signals into a
deterministic portfolio holding score.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioScoreSnapshot:
    """Scored portfolio holding."""

    symbol: str
    score: int
    classification: str
    confidence: float


class PortfolioScoringEngine:
    """Score individual portfolio holdings."""

    @staticmethod
    def _value(
        holding: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from a dict or object."""

        if isinstance(holding, dict):
            return holding.get(field, default)

        return getattr(holding, field, default)

    @staticmethod
    def classify(score: int) -> str:
        """Classify a portfolio holding score."""

        if score >= 8:
            return "STRONG"
        if score >= 3:
            return "POSITIVE"
        if score <= -8:
            return "VERY WEAK"
        if score < 0:
            return "WEAK"
        return "NEUTRAL"

    def analyze(
        self,
        holding: Any,
    ) -> PortfolioScoreSnapshot | None:
        """Score a single portfolio holding.

        Existing holding objects are not mutated.
        None holdings return None.
        """

        if holding is None:
            return None

        symbol = self._value(holding, "symbol", "")

        # ✅ Extract individual component scores
        strength_score = int(self._value(holding, "strength_score", 0))
        momentum_score = int(self._value(holding, "momentum_score", 0))
        volume_score = int(self._value(holding, "volume_score", 0))
        signal_score = int(self._value(holding, "signal_score", 0))

        confidence = float(self._value(holding, "confidence", 0))

        # ✅ Clean implementation: add weighting only for extreme strength cases
        score = (
            strength_score
            + momentum_score
            + volume_score
            + signal_score
        )

        if strength_score == 2:
            score += 2
        elif strength_score == -2:
            score -= 2

        return PortfolioScoreSnapshot(
            symbol=symbol,
            score=score,
            classification=self.classify(score),
            confidence=confidence,
        )
