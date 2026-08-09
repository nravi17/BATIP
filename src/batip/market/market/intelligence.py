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
    breadth_score: int
    total_score: int

    sector_count: int
    stock_count: int

    breadth_advances: int | None = None
    breadth_declines: int | None = None
    breadth_unchanged: int | None = None


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

    @staticmethod
    def _value(item, field, default=0):
        """Helper to safely extract values from objects or dicts."""
        if isinstance(item, dict):
            return item.get(field, default)
        return getattr(item, field, default)

    def analyze(
        self,
        sectors: list[SectorSnapshot],
        stocks: list[StockIntelligenceSnapshot],
        breadth_advances: int | None = None,
        breadth_declines: int | None = None,
        breadth_unchanged: int | None = None,
    ) -> MarketIntelligenceSnapshot:
        """Aggregate sector and stock intelligence."""

        valid_sectors = [sector for sector in sectors if sector is not None]
        valid_stocks = [stock for stock in stocks if stock is not None]

        strongest_sector = None
        weakest_sector = None

        if valid_sectors:
            strongest = max(
                valid_sectors,
                key=lambda sector: (
                    self._value(sector, "score"),
                    self._value(sector, "change_percent"),
                    self._value(sector, "symbol", ""),
                ),
            )

            weakest = min(
                valid_sectors,
                key=lambda sector: (
                    self._value(sector, "score"),
                    self._value(sector, "change_percent"),
                    self._value(sector, "symbol", ""),
                ),
            )

            strongest_sector = self._value(strongest, "symbol", None)
            weakest_sector = self._value(weakest, "symbol", None)

        top_stock = None
        if valid_stocks:
            strongest_stock = max(
                valid_stocks,
                key=lambda stock: (
                    self._value(stock, "total_score"),
                    self._value(stock, "confidence"),
                    self._value(stock, "symbol", ""),
                ),
            )
            top_stock = self._value(strongest_stock, "symbol", None)

        sector_score = sum(self._value(sector, "score") for sector in valid_sectors)
        stock_score = sum(self._value(stock, "total_score") for stock in valid_stocks)

        # --------------------------------------------------------------
        # Breadth scoring
        # --------------------------------------------------------------
        breadth_score = 0
        if breadth_advances is not None and breadth_declines is not None:
            total = breadth_advances + breadth_declines + (breadth_unchanged or 0)
            if total > 0:
                advance_ratio = breadth_advances / total
                decline_ratio = breadth_declines / total

                if advance_ratio >= 0.60:
                    breadth_score = 2
                elif advance_ratio >= 0.50:
                    breadth_score = 1
                elif decline_ratio >= 0.60:
                    breadth_score = -2
                elif decline_ratio >= 0.50:
                    breadth_score = -1

        total_score = sector_score + stock_score + breadth_score

        return MarketIntelligenceSnapshot(
            market_bias=self.classify_bias(total_score),
            strongest_sector=strongest_sector,
            weakest_sector=weakest_sector,
            top_stock=top_stock,
            sector_score=sector_score,
            stock_score=stock_score,
            breadth_score=breadth_score,
            total_score=total_score,
            sector_count=len(valid_sectors),
            stock_count=len(valid_stocks),
            breadth_advances=breadth_advances,
            breadth_declines=breadth_declines,
            breadth_unchanged=breadth_unchanged,
        )

