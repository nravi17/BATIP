"""
BATIP Portfolio Capital Allocation Intelligence.

Determines position sizing and capital allocation from portfolio
risk, available capital, entry price, stop loss, and allocation limits.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioAllocationSnapshot:
    """Final portfolio capital allocation plan."""

    symbol: str
    action: str
    available_capital: float
    risk_budget: float
    risk_per_share: float
    position_size: int
    capital_required: float
    allocation_percent: float
    max_allocation_percent: float
    exposure_percent: float
    allocation_status: str
    confidence: float


class PortfolioAllocationEngine:
    """Generate deterministic portfolio capital allocations."""

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from a dict or object."""

        if isinstance(data, dict):
            return data.get(field, default)

        return getattr(data, field, default)

    def analyze(
        self,
        data: Any,
    ) -> PortfolioAllocationSnapshot | None:
        """Generate a portfolio capital allocation."""

        if data is None:
            return None

        symbol = str(
            self._value(data, "symbol", "")
        )

        action = str(
            self._value(data, "action", "WATCH")
        ).upper()

        available_capital = float(
            self._value(data, "available_capital", 0)
        )

        entry_price = float(
            self._value(data, "entry_price", 0)
        )

        stop_loss = float(
            self._value(data, "stop_loss", 0)
        )

        risk_percent = float(
            self._value(data, "risk_percent", 1.0)
        )

        max_allocation_percent = float(
            self._value(data, "max_allocation_percent", 20.0)
        )

        confidence = float(
            self._value(data, "confidence", 0)
        )

        # ---------------------------------------------------------
        # Risk budget
        # ---------------------------------------------------------

        risk_budget = (
            available_capital
            * risk_percent
            / 100
        )

        # ---------------------------------------------------------
        # Risk per share
        # ---------------------------------------------------------

        risk_per_share = abs(
            entry_price - stop_loss
        )

        # ---------------------------------------------------------
        # Invalid inputs
        # ---------------------------------------------------------

        if (
            available_capital <= 0
            or entry_price <= 0
            or risk_per_share <= 0
        ):
            return PortfolioAllocationSnapshot(
                symbol=symbol,
                action=action,
                available_capital=available_capital,
                risk_budget=round(risk_budget, 2),
                risk_per_share=round(
                    max(risk_per_share, 0),
                    2,
                ),
                position_size=0,
                capital_required=0.0,
                allocation_percent=0.0,
                max_allocation_percent=max_allocation_percent,
                exposure_percent=0.0,
                allocation_status="INVALID",
                confidence=confidence,
            )

        # ---------------------------------------------------------
        # Risk-based position size
        # ---------------------------------------------------------

        risk_position_size = int(
            risk_budget / risk_per_share
        )

        # ---------------------------------------------------------
        # Capital allocation limit
        # ---------------------------------------------------------

        max_capital_allocation = (
            available_capital
            * max_allocation_percent
            / 100
        )

        allocation_position_size = int(
            max_capital_allocation
            / entry_price
        )

        # Final position size is constrained by both:
        #
        # 1. Risk budget
        # 2. Maximum capital allocation
        #

        position_size = min(
            risk_position_size,
            allocation_position_size,
        )

        capital_required = (
            position_size * entry_price
        )

        allocation_percent = (
            capital_required
            / available_capital
            * 100
        )

        exposure_percent = allocation_percent

        # ---------------------------------------------------------
        # Allocation status
        # ---------------------------------------------------------

        allocation_status = "VALID"

        if action not in {
            "BUY",
            "STRONG BUY",
        }:
            allocation_status = "NOT_ACTIONABLE"

        elif position_size <= 0:
            allocation_status = "INVALID"

        elif allocation_percent > max_allocation_percent:
            allocation_status = "LIMIT_EXCEEDED"

        return PortfolioAllocationSnapshot(
            symbol=symbol,
            action=action,
            available_capital=available_capital,
            risk_budget=round(
                risk_budget,
                2,
            ),
            risk_per_share=round(
                risk_per_share,
                2,
            ),
            position_size=position_size,
            capital_required=round(
                capital_required,
                2,
            ),
            allocation_percent=round(
                allocation_percent,
                2,
            ),
            max_allocation_percent=round(
                max_allocation_percent,
                2,
            ),
            exposure_percent=round(
                exposure_percent,
                2,
            ),
            allocation_status=allocation_status,
            confidence=confidence,
        )