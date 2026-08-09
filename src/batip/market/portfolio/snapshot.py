"""
BATIP Portfolio Snapshot Engine.

Builds a deterministic snapshot of portfolio value,
P&L, holding count, and sector exposure.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioSnapshot:
    """Aggregated portfolio snapshot."""

    total_invested: float
    total_value: float
    total_pnl: float
    total_pnl_percent: float

    holding_count: int

    sector_exposure: dict[str, float]


class PortfolioSnapshotEngine:
    """Analyze portfolio holdings."""

    @staticmethod
    def _value(
        holding: Any,
        field: str,
        default: Any = None,
    ) -> Any:
        """Safely extract a value from a dict or object."""

        if isinstance(holding, dict):
            return holding.get(field, default)

        return getattr(holding, field, default)

    def analyze(
        self,
        holdings: list[Any],
    ) -> PortfolioSnapshot:
        """Build a portfolio snapshot.

        Existing holding objects are not mutated.
        None holdings are ignored.
        """

        if not holdings:
            return PortfolioSnapshot(
                total_invested=0,
                total_value=0,
                total_pnl=0,
                total_pnl_percent=0,
                holding_count=0,
                sector_exposure={},
            )

        total_invested = 0.0
        total_value = 0.0
        sector_exposure: dict[str, float] = {}

        valid_holdings = [
            holding
            for holding in holdings
            if holding is not None
        ]

        for holding in valid_holdings:
            quantity = float(
                self._value(holding, "quantity", 0)
            )

            average_price = float(
                self._value(holding, "average_price", 0)
            )

            current_price = float(
                self._value(holding, "current_price", 0)
            )

            invested = quantity * average_price
            value = quantity * current_price

            total_invested += invested
            total_value += value

            sector = self._value(
                holding,
                "sector",
                None,
            )

            if sector:
                sector_exposure[sector] = (
                    sector_exposure.get(sector, 0.0)
                    + value
                )

        total_pnl = total_value - total_invested

        if total_invested:
            total_pnl_percent = (
                total_pnl / total_invested
            ) * 100
        else:
            total_pnl_percent = 0

        return PortfolioSnapshot(
            total_invested=total_invested,
            total_value=total_value,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            holding_count=len(valid_holdings),
            sector_exposure=sector_exposure,
        )