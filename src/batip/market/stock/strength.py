"""
BATIP Stock Strength Engine.

Provides deterministic stock scoring and ranking.
"""

from batip.market.stock.scanner import StockSnapshot


class StockStrengthEngine:
    """Analyze and rank market stocks."""

    @staticmethod
    def score_stock(change_percent: float) -> int:
        """Convert stock percentage movement into a normalized score."""
        change = float(change_percent)

        if change >= 1.0:
            return 2
        if change > 0:
            return 1
        if change <= -1.0:
            return -2
        if change < 0:
            return -1
        return 0

    def analyze(
        self,
        stocks: list[StockSnapshot],
    ) -> list[StockSnapshot]:
        """Score and rank stocks without mutating originals."""

        if not stocks:
            return []

        analyzed: list[StockSnapshot] = []

        for stock in stocks:
            if stock is None:
                continue

            score = self.score_stock(stock.change_percent)

            analyzed.append(
                StockSnapshot(
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
                    direction="Bullish" if score > 0 else "Bearish" if score < 0 else "Neutral",
                    recommendation="WATCH",  # Strength engine only scores, scanner handles full recommendation
                )
            )

        analyzed.sort(
            key=lambda stock: (
                stock.score,
                stock.change_percent,
                stock.symbol,
            ),
            reverse=True,
        )

        return analyzed

    @staticmethod
    def strongest(
        stocks: list[StockSnapshot],
    ) -> StockSnapshot | None:
        """Return the strongest stock."""
        if not stocks:
            return None

        return max(
            stocks,
            key=lambda stock: (
                stock.score,
                stock.change_percent,
            ),
        )

    @staticmethod
    def weakest(
        stocks: list[StockSnapshot],
    ) -> StockSnapshot | None:
        """Return the weakest stock."""
        if not stocks:
            return None

        return min(
            stocks,
            key=lambda stock: (
                stock.score,
                stock.change_percent,
            ),
        )
