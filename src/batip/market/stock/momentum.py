"""
BATIP Stock Momentum Engine.

Provides deterministic momentum scoring,
direction classification, and acceleration analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockMomentumSnapshot:
    """Normalized stock momentum snapshot."""

    symbol: str
    momentum_percent: float
    previous_momentum_percent: float = 0.0
    score: int = 0
    direction: str = "Neutral"
    momentum_change: float = 0.0
    acceleration: str = "Stable"


class StockMomentumEngine:
    """Analyze stock momentum."""

    @staticmethod
    def score_momentum(momentum_percent: float) -> int:
        """
        Convert momentum percentage into a normalized score.

        Rules:
            >= +1.0% -> +2
            >   0%   -> +1
            == 0%    ->  0
            <   0%   -> -1
            <= -1.0% -> -2
        """

        momentum = float(momentum_percent)

        if momentum >= 1.0:
            return 2

        if momentum > 0:
            return 1

        if momentum <= -1.0:
            return -2

        if momentum < 0:
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        """Convert momentum score into market direction."""

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def acceleration_from_change(momentum_change: float) -> str:
        """Classify momentum acceleration."""

        change = float(momentum_change)

        if change > 0:
            return "Accelerating"

        if change < 0:
            return "Decelerating"

        return "Stable"

    def analyze(
        self,
        momentum: StockMomentumSnapshot,
    ) -> StockMomentumSnapshot:
        """Analyze a stock momentum snapshot."""

        if momentum is None:
            raise ValueError("momentum cannot be None")

        current = float(momentum.momentum_percent)
        previous = float(momentum.previous_momentum_percent)

        score = self.score_momentum(current)
        direction = self.direction_from_score(score)

        momentum_change = current - previous

        acceleration = self.acceleration_from_change(
            momentum_change
        )

        return StockMomentumSnapshot(
            symbol=momentum.symbol,
            momentum_percent=current,
            previous_momentum_percent=previous,
            score=score,
            direction=direction,
            momentum_change=momentum_change,
            acceleration=acceleration,
        )