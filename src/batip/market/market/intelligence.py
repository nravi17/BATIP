"""
BATIP Market Intelligence Engine.

Aggregates sector and stock intelligence into
a deterministic overall market view.
"""

from dataclasses import dataclass

from batip.market.sector import SectorSnapshot
from batip.market.stock import StockIntelligenceSnapshot


@dataclass(frozen=True)
class MarketIntelligenceSnapshot:
    """Aggregated market intelligence."""

    market_bias: str

    strongest_sector: str | None
    weakest_sector: str | None

    top_stock: str | None

    sector_score: int
    stock_score: int
    total_score: int

    sector_count: int
    stock_count: int


class MarketIntelligenceEngine:
    """Analyze overall market intelligence."""

    @staticmethod
    def classify_bias(total_score: int) -> str:
        """Convert total market score into a market bias."""

        if total_score > 0:
            return "Bullish"

        if total_score < 0:
            return "Bearish"

        return "Neutral"

    def analyze(
        self,
        sectors: list[SectorSnapshot],
        stocks: list[StockIntelligenceSnapshot],
    ) -> MarketIntelligenceSnapshot:
        """Aggregate sector and stock intelligence."""

        valid_sectors = [
            sector
            for sector in sectors
            if sector is not None
        ]

        valid_stocks = [
            stock
            for stock in stocks
            if stock is not None
        ]

        strongest_sector = None
        weakest_sector = None

        if valid_sectors:
            strongest = max(
                valid_sectors,
                key=lambda sector: (
                    sector.score,
                    sector.change_percent,
                    sector.symbol,
                ),
            )

            weakest = min(
                valid_sectors,
                key=lambda sector: (
                    sector.score,
                    sector.change_percent,
                    sector.symbol,
                ),
            )

            strongest_sector = strongest.symbol
            weakest_sector = weakest.symbol

        top_stock = None

        if valid_stocks:
            strongest_stock = max(
                valid_stocks,
                key=lambda stock: (
                    stock.total_score,
                    stock.confidence,
                    stock.symbol,
                ),
            )

            top_stock = strongest_stock.symbol

        sector_score = sum(
            sector.score
            for sector in valid_sectors
        )

        stock_score = sum(
            stock.total_score
            for stock in valid_stocks
        )

        total_score = sector_score + stock_score

        return MarketIntelligenceSnapshot(
            market_bias=self.classify_bias(total_score),
            strongest_sector=strongest_sector,
            weakest_sector=weakest_sector,
            top_stock=top_stock,
            sector_score=sector_score,
            stock_score=stock_score,
            total_score=total_score,
            sector_count=len(valid_sectors),
            stock_count=len(valid_stocks),
        )
