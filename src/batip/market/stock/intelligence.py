"""
BATIP Stock Intelligence Engine.

Combines sector, strength, momentum, volume and signal
scores into a unified stock intelligence snapshot.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockIntelligenceSnapshot:
    """Unified stock intelligence result."""

    symbol: str
    name: str
    sector: str

    sector_score: int
    strength_score: int
    momentum_score: int
    volume_score: int
    signal_score: int

    total_score: int
    direction: str
    recommendation: str
    confidence: float


class StockIntelligenceEngine:
    """Aggregate stock-level intelligence."""

    @staticmethod
    def direction_from_score(score: int) -> str:
        if score > 0:
            return "Bullish"
        if score < 0:
            return "Bearish"
        return "Neutral"

    @staticmethod
    def recommendation_from_score(score: int) -> str:
        if score >= 8:
            return "STRONG BUY"
        if score >= 3:
            return "BUY"
        if score <= -8:
            return "STRONG SELL"
        if score <= -3:
            return "SELL"
        return "WATCH"

    @staticmethod
    def calculate_confidence(scores: list[int]) -> float:
        """
        Calculate confidence from signal strength and
        directional agreement.
        """

        if not scores:
            return 0.0

        maximum_score = len(scores) * 2
        total_magnitude = sum(abs(score) for score in scores)

        magnitude_ratio = total_magnitude / maximum_score

        bullish = sum(1 for score in scores if score > 0)
        bearish = sum(1 for score in scores if score < 0)

        if bullish == 0 and bearish == 0:
            return 0.0

        dominant_count = max(bullish, bearish)
        opposing_count = min(bullish, bearish)

        alignment_ratio = (dominant_count - opposing_count) / len(scores)

        confidence = (
            magnitude_ratio * 70
            + max(alignment_ratio, 0) * 30
        )

        return round(confidence, 2)

    def analyze(
        self,
        symbol: str,
        name: str,
        sector: str,
        sector_score: int,
        strength_score: int,
        momentum_score: int,
        volume_score: int,
        signal_score: int,
    ) -> StockIntelligenceSnapshot:
        """Build unified stock intelligence."""

        scores = [
            int(sector_score),
            int(strength_score),
            int(momentum_score),
            int(volume_score),
            int(signal_score),
        ]

        total_score = sum(scores)

        direction = self.direction_from_score(total_score)
        recommendation = self.recommendation_from_score(total_score)
        confidence = self.calculate_confidence(scores)

        return StockIntelligenceSnapshot(
            symbol=symbol,
            name=name,
            sector=sector,
            sector_score=int(sector_score),
            strength_score=int(strength_score),
            momentum_score=int(momentum_score),
            volume_score=int(volume_score),
            signal_score=int(signal_score),
            total_score=total_score,
            direction=direction,
            recommendation=recommendation,
            confidence=confidence,
        )

    @staticmethod
    def rank(
        stocks: list[StockIntelligenceSnapshot],
    ) -> list[StockIntelligenceSnapshot]:
        """Rank stocks from strongest to weakest."""

        if not stocks:
            return []

        valid_stocks = [stock for stock in stocks if stock is not None]

        return sorted(
            valid_stocks,
            key=lambda stock: (
                stock.total_score,
                stock.confidence,
                stock.symbol,
            ),
            reverse=True,
        )
