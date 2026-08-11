"""
BATIP Stock Snapshot Intelligence.

Creates a deterministic snapshot of stock-level
market intelligence.
"""

from typing import Any
from batip.market.stock.scanner import StockSnapshot


class StockSnapshotEngine:
    """Build deterministic stock snapshots."""

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from dictionaries or objects."""

        if isinstance(data, dict):
            return data.get(field, default)

        return getattr(data, field, default)

    @staticmethod
    def score_stock(change_percent: float) -> int:
        """
        Convert stock percentage movement into a normalized score.

        Rules:
            >= +1.0% -> +2
            >   0%   -> +1
            == 0%    ->  0
            <   0%   -> -1
            <= -1.0% -> -2
        """

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

    @staticmethod
    def direction_from_score(score: int) -> str:
        """Convert normalized stock score into direction."""

        if score > 0:
            return "Bullish"
        if score < 0:
            return "Bearish"
        return "Neutral"

    def analyze(
        self,
        data: Any,
    ) -> StockSnapshot | None:
        """Create a stock snapshot without mutating the input."""

        if data is None:
            return None

        symbol = str(self._value(data, "symbol", ""))
        name = str(self._value(data, "name", symbol))
        sector = str(self._value(data, "sector", ""))

        price = float(self._value(data, "price", 0.0))
        change_percent = float(self._value(data, "change_percent", 0.0))
        volume = int(self._value(data, "volume", 0))

        market_bias = str(self._value(data, "market_bias", "Neutral"))
        confidence = float(self._value(data, "confidence", 0.0))

        score = self.score_stock(change_percent)
        direction = self.direction_from_score(score)

        return StockSnapshot(
            symbol=symbol,
            name=name,
            sector=sector,
            price=price,
            change_percent=change_percent,
            volume=volume,
            score=score,
            direction=direction,
            market_bias=market_bias,
            confidence=confidence,
)