"""
BATIP Portfolio Allocator.

Selects paper-trading candidates while enforcing:
- maximum number of positions
- maximum portfolio risk
- available capital limits

No broker connectivity and no order execution.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PortfolioAllocation:
    """Result of portfolio allocation."""

    positions: list[dict[str, Any]] = field(default_factory=list)
    total_risk: float = 0.0
    total_capital_deployed: float = 0.0
    remaining_capital: float = 0.0
    valid: bool = True


class PortfolioAllocator:
    """Allocate trade candidates into a paper-trading portfolio."""

    def __init__(
        self,
        capital: float = 100000.0,
        max_portfolio_risk_percent: float = 3.0,
        max_positions: int = 3,
    ) -> None:
        self.capital = float(capital)
        self.max_portfolio_risk_percent = float(
            max_portfolio_risk_percent
        )
        self.max_positions = int(max_positions)

    @property
    def max_portfolio_risk(self) -> float:
        """Maximum allowed monetary portfolio risk."""

        if self.capital <= 0:
            return 0.0

        if self.max_portfolio_risk_percent <= 0:
            return 0.0

        return (
            self.capital
            * self.max_portfolio_risk_percent
            / 100.0
        )

    @staticmethod
    def _capital_required(candidate: dict[str, Any]) -> float:
        """Calculate capital required for a candidate."""

        position_size = candidate.get("position_size", 0)
        entry = candidate.get("entry", 0)

        try:
            position_size = float(position_size)
            entry = float(entry)
        except (TypeError, ValueError):
            return 0.0

        if position_size <= 0 or entry <= 0:
            return 0.0

        return position_size * entry

    @staticmethod
    def _maximum_loss(candidate: dict[str, Any]) -> float:
        """Get candidate maximum loss."""

        try:
            maximum_loss = float(
                candidate.get("maximum_loss", 0)
            )
        except (TypeError, ValueError):
            return 0.0

        return max(maximum_loss, 0.0)

    @staticmethod
    def _score(candidate: dict[str, Any]) -> float:
        """Get candidate score used for ranking."""

        try:
            return float(candidate.get("score", 0))
        except (TypeError, ValueError):
            return 0.0

    def allocate(
        self,
        candidates: list[dict[str, Any]],
    ) -> PortfolioAllocation:
        """Select candidates that fit portfolio constraints."""

        result = PortfolioAllocation(
            remaining_capital=max(self.capital, 0.0),
        )

        if self.capital <= 0:
            result.valid = False
            return result

        if self.max_positions <= 0:
            result.valid = False
            return result

        if self.max_portfolio_risk <= 0:
            result.valid = False
            return result

        if not candidates:
            return result

        # Only TRADE candidates are eligible.
        eligible = [
            candidate
            for candidate in candidates
            if str(candidate.get("action", "")).strip().upper()
            == "TRADE"
        ]

        # Highest score first.
        eligible.sort(
            key=self._score,
            reverse=True,
        )

        for candidate in eligible:
            if len(result.positions) >= self.max_positions:
                break

            capital_required = self._capital_required(candidate)
            candidate_risk = self._maximum_loss(candidate)

            # Invalid candidate data cannot be allocated.
            if capital_required <= 0:
                continue

            if candidate_risk <= 0:
                continue

            # Do not exceed available capital.
            if (
                result.total_capital_deployed
                + capital_required
                > self.capital
            ):
                continue

            # Do not exceed portfolio risk.
            if (
                result.total_risk + candidate_risk
                > self.max_portfolio_risk
            ):
                continue

            result.positions.append(candidate)
            result.total_risk += candidate_risk
            result.total_capital_deployed += capital_required

        result.remaining_capital = (
            self.capital - result.total_capital_deployed
        )

        result.valid = (
            result.total_risk <= self.max_portfolio_risk
            and result.total_capital_deployed <= self.capital
            and len(result.positions) <= self.max_positions
        )

        return result