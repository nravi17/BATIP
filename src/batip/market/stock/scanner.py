"""
BATIP Stock Scanner.

Provides deterministic multi-factor stock intelligence.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockSnapshot:
    """Normalized stock market snapshot."""

    symbol: str
    name: str = ""
    sector: str = ""   # ✅ Added canonical sector field
    price: float = 0.0
    change_percent: float = 0.0
    momentum: float = 0.0
    volume: float = 0.0
    volume_change_percent: float = 0.0
    sector_score: int = 0
    liquidity_score: int = 0

    score: int = 0
    direction: str = "Neutral"
    recommendation: str = "WATCH"
    market_bias: str = "Neutral"
    confidence: float = 0.0

class StockScanner:
    """Deterministic stock scoring and ranking engine."""

    # ------------------------------------------------------------------
    # FACTOR SCORING
    # ------------------------------------------------------------------

    @staticmethod
    def price_score(change_percent: float) -> int:
        change = float(change_percent)

        if change >= 2.0:
            return 2
        if change > 0:
            return 1
        if change <= -2.0:
            return -2
        if change < 0:
            return -1
        return 0

    @staticmethod
    def momentum_score(momentum: float) -> int:
        value = float(momentum)

        if value >= 2.0:
            return 2
        if value > 0:
            return 1
        if value <= -2.0:
            return -2
        if value < 0:
            return -1
        return 0

    @staticmethod
    def volume_score(volume_change_percent: float) -> int:
        value = float(volume_change_percent)

        if value >= 50:
            return 2
        if value > 0:
            return 1
        if value <= -50:
            return -2
        if value < 0:
            return -1
        return 0

    # ------------------------------------------------------------------
    # RECOMMENDATION / DIRECTION
    # ------------------------------------------------------------------

    @staticmethod
    def recommendation_from_score(score: int) -> str:
        if score >= 8:
            return "STRONG BUY"
        if score >= 4:
            return "BUY"
        if score <= -8:
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

    # ------------------------------------------------------------------
    # ANALYSIS
    # ------------------------------------------------------------------

    def analyze(self, stock: StockSnapshot) -> StockSnapshot:
        """
        Analyze one stock.

        Existing StockSnapshot objects are not mutated.
        """

        price = self.price_score(stock.change_percent)
        momentum = self.momentum_score(stock.momentum)
        volume = self.volume_score(stock.volume_change_percent)

        score = (
            price
            + momentum
            + volume
            + stock.sector_score
            + stock.liquidity_score
        )

        return StockSnapshot(
            symbol=stock.symbol,
            name=stock.name,
            sector=stock.sector,  # ✅ sector preserved
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

    # ------------------------------------------------------------------
    # RANKING
    # ------------------------------------------------------------------

    def rank(self, stocks: list[StockSnapshot]) -> list[StockSnapshot]:
        """
        Analyze and rank stocks from strongest to weakest.
        """

        if not stocks:
            return []

        analyzed = [
            self.analyze(stock)
            for stock in stocks
            if stock is not None
        ]

        analyzed.sort(
            key=lambda stock: (
                stock.score,
                stock.change_percent,
                stock.symbol,
            ),
            reverse=True,
        )

        return analyzed
