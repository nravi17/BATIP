"""
BATIP Stock Intelligence.

Pure scoring layer for individual stocks.

This module does not fetch market data and does not place trades.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class StockSnapshot:
    """Normalized stock market snapshot."""

    symbol: str
    name: str = ""

    # Price / momentum
    price: float = 0.0
    change_percent: float = 0.0
    momentum: float = 0.0

    # Volume
    volume: float = 0.0
    volume_change_percent: float = 0.0

    # Context
    sector_score: int = 0
    liquidity_score: int = 0

    # Derived fields
    score: int = 0
    direction: str = "Neutral"
    recommendation: str = "WATCH"


class StockScanner:
    """Score and rank individual stocks."""

    @staticmethod
    def price_score(change_percent: float) -> int:
        if change_percent >= 2.0:
            return 2

        if change_percent > 0:
            return 1

        if change_percent <= -2.0:
            return -2

        if change_percent < 0:
            return -1

        return 0

    @staticmethod
    def momentum_score(momentum: float) -> int:
        if momentum >= 2.0:
            return 2

        if momentum > 0:
            return 1

        if momentum <= -2.0:
            return -2

        if momentum < 0:
            return -1

        return 0

    @staticmethod
    def volume_score(volume_change_percent: float) -> int:
        if volume_change_percent >= 50:
            return 2

        if volume_change_percent > 0:
            return 1

        if volume_change_percent <= -50:
            return -2

        if volume_change_percent < 0:
            return -1

        return 0

    @staticmethod
    def recommendation_from_score(score: int) -> str:
        if score >= 7:
            return "STRONG BUY"

        if score >= 4:
            return "BUY"

        if score <= -7:
            return "STRONG SELL"

        if score <= -4:
            return "SELL"

        return "WATCH"

    @staticmethod
    def direction_from_score(score: int) -> str:
        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    def analyze(self, stock: StockSnapshot) -> StockSnapshot:
        """Calculate the stock opportunity score."""

        score = 0

        score += self.price_score(
            stock.change_percent
        )

        score += self.momentum_score(
            stock.momentum
        )

        score += self.volume_score(
            stock.volume_change_percent
        )

        score += stock.sector_score
        score += stock.liquidity_score

        return StockSnapshot(
            symbol=stock.symbol,
            name=stock.name,
            price=stock.price,
            change_percent=stock.change_percent,
            momentum=stock.momentum,
            volume=stock.volume,
            volume_change_percent=stock.volume_change_percent,
            sector_score=stock.sector_score,
            liquidity_score=stock.liquidity_score,
            score=score,
            direction=self.direction_from_score(score),
            recommendation=self.recommendation_from_score(score),
        )

    def rank(
        self,
        stocks: list[StockSnapshot],
    ) -> list[StockSnapshot]:
        """Analyze and rank stocks by score."""

        analyzed = [
            self.analyze(stock)
            for stock in stocks
        ]

        return sorted(
            analyzed,
            key=lambda stock: stock.score,
            reverse=True,
        )