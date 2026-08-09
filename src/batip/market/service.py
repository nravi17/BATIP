"""
BATIP Market Service.

Orchestrates market-level analysis using the existing BATIP
market components.

This layer does not fetch data from external brokers or APIs.
It operates on the market objects already available inside BATIP.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class MarketSummary:
    """High-level market summary."""

    market: str
    total_symbols: int
    bullish_symbols: int
    bearish_symbols: int
    neutral_symbols: int
    average_change: float
    breadth: str


class MarketService:
    """
    Orchestrates market analysis.

    The service accepts flexible symbol records so it can work with
    existing BATIP market models without tightly coupling this layer
    to a particular data provider.
    """

    def __init__(self) -> None:
        self._symbols: list[Any] = []

    @property
    def symbols(self) -> list[Any]:
        """Return a copy of the currently loaded symbols."""
        return list(self._symbols)

    def load_symbols(self, symbols: Iterable[Any]) -> int:
        """
        Load market symbol records.

        Existing records are replaced.

        Returns:
            Number of loaded records.
        """
        if symbols is None:
            self._symbols = []
            return 0

        self._symbols = list(symbols)
        return len(self._symbols)

    def add_symbol(self, symbol: Any) -> None:
        """Add a single symbol record."""
        if symbol is None:
            raise ValueError("Symbol cannot be None")

        self._symbols.append(symbol)

    def clear(self) -> None:
        """Remove all loaded market symbols."""
        self._symbols.clear()

    @staticmethod
    def _get_value(
        record: Any,
        *names: str,
        default: Any = None,
    ) -> Any:
        """
        Read a value from either an object or a dictionary.

        This keeps the service compatible with both dataclass/model
        objects and dictionary-based market data.
        """
        for name in names:
            if isinstance(record, dict):
                if name in record:
                    return record[name]

            if hasattr(record, name):
                return getattr(record, name)

        return default

    @classmethod
    def symbol_name(cls, record: Any) -> str:
        """Return a normalized symbol name."""
        value = cls._get_value(
            record,
            "symbol",
            "ticker",
            "name",
            default="",
        )

        if value is None:
            return ""

        return str(value).strip().upper()

    @classmethod
    def price_change(cls, record: Any) -> float:
        """Return percentage price change for a symbol."""
        value = cls._get_value(
            record,
            "change_percent",
            "change_pct",
            "percentage_change",
            "pct_change",
            "change",
            default=0.0,
        )

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @classmethod
    def classify_symbol(cls, record: Any) -> str:
        """
        Classify a symbol based on percentage change.

        Returns:
            BULLISH, BEARISH, or NEUTRAL.
        """
        change = cls.price_change(record)

        if change > 0:
            return "BULLISH"

        if change < 0:
            return "BEARISH"

        return "NEUTRAL"

    def bullish_symbols(self) -> list[Any]:
        """Return symbols with positive price change."""
        return [
            symbol
            for symbol in self._symbols
            if self.classify_symbol(symbol) == "BULLISH"
        ]

    def bearish_symbols(self) -> list[Any]:
        """Return symbols with negative price change."""
        return [
            symbol
            for symbol in self._symbols
            if self.classify_symbol(symbol) == "BEARISH"
        ]

    def neutral_symbols(self) -> list[Any]:
        """Return symbols with zero price change."""
        return [
            symbol
            for symbol in self._symbols
            if self.classify_symbol(symbol) == "NEUTRAL"
        ]

    def average_change(self) -> float:
        """Calculate the average percentage change."""
        if not self._symbols:
            return 0.0

        total = sum(
            self.price_change(symbol)
            for symbol in self._symbols
        )

        return total / len(self._symbols)

    def breadth(self) -> str:
        """
        Determine overall market breadth.

        Returns:
            BULLISH, BEARISH, or NEUTRAL.

        Equal bullish/bearish counts are treated as NEUTRAL.
        """
        bullish = len(self.bullish_symbols())
        bearish = len(self.bearish_symbols())

        if bullish > bearish:
            return "BULLISH"

        if bearish > bullish:
            return "BEARISH"

        return "NEUTRAL"

    def summary(self, market: str = "NSE") -> MarketSummary:
        """Build a high-level market summary."""
        if market is None:
            market = "NSE"

        market_name = str(market).strip().upper()

        return MarketSummary(
            market=market_name,
            total_symbols=len(self._symbols),
            bullish_symbols=len(self.bullish_symbols()),
            bearish_symbols=len(self.bearish_symbols()),
            neutral_symbols=len(self.neutral_symbols()),
            average_change=round(self.average_change(), 2),
            breadth=self.breadth(),
        )

    def get_symbol(self, symbol: str) -> Optional[Any]:
        """
        Find a loaded symbol by symbol/ticker/name.

        Returns:
            Matching record or None.
        """
        if symbol is None:
            return None

        target = str(symbol).strip().upper()

        if not target:
            return None

        for record in self._symbols:
            if self.symbol_name(record) == target:
                return record

        return None

    def analyze(
        self,
        symbols: Optional[Iterable[Any]] = None,
        market: str = "NSE",
    ) -> MarketSummary:
        """
        Analyze market data.

        If symbols are provided, they replace the currently loaded
        records before analysis.
        """
        if symbols is not None:
            self.load_symbols(symbols)

        return self.summary(market=market)