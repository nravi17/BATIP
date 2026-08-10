"""
BATIP Portfolio Execution Intelligence.

Converts a portfolio decision into a deterministic execution plan.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioExecutionSnapshot:
    """Final portfolio execution plan."""

    symbol: str
    action: str
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_per_share: float
    risk_reward: float
    position_size: int
    capital_required: float
    max_loss: float
    execution_status: str
    confidence: float


class PortfolioExecutionEngine:
    """Generate deterministic portfolio execution plans."""

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
    ) -> PortfolioExecutionSnapshot | None:
        """Generate an execution plan."""

        if data is None:
            return None

        symbol = str(self._value(data, "symbol", ""))

        action = str(
            self._value(data, "action", "WATCH")
        ).upper()

        entry_price = float(
            self._value(data, "entry_price", 0)
        )

        stop_loss = float(
            self._value(data, "stop_loss", 0)
        )

        target_1 = float(
            self._value(data, "target_1", 0)
        )

        target_2 = float(
            self._value(data, "target_2", 0)
        )

        capital = float(
            self._value(data, "capital", 0)
        )

        risk_percent = float(
            self._value(data, "risk_percent", 1.0)
        )

        confidence = float(
            self._value(data, "confidence", 0)
        )

        # ---------------------------------------------------------
        # No valid entry price
        # ---------------------------------------------------------

        if entry_price <= 0:
            return PortfolioExecutionSnapshot(
                symbol=symbol,
                action=action,
                entry_price=entry_price,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                risk_per_share=0.0,
                risk_reward=0.0,
                position_size=0,
                capital_required=0.0,
                max_loss=0.0,
                execution_status="INVALID",
                confidence=confidence,
            )

        # ---------------------------------------------------------
        # Risk per share
        # ---------------------------------------------------------

        risk_per_share = abs(entry_price - stop_loss)

        # ---------------------------------------------------------
        # Position sizing
        # ---------------------------------------------------------

        max_loss = capital * (risk_percent / 100)

        if risk_per_share > 0:
            position_size = int(
                max_loss / risk_per_share
            )
        else:
            position_size = 0

        capital_required = (
            position_size * entry_price
        )

        actual_max_loss = (
            position_size * risk_per_share
        )

        # ---------------------------------------------------------
        # Risk / reward
        # ---------------------------------------------------------

        reward = max(
            target_1 - entry_price,
            0,
        )

        if risk_per_share > 0:
            risk_reward = reward / risk_per_share
        else:
            risk_reward = 0.0

        # ---------------------------------------------------------
        # Execution validation
        # ---------------------------------------------------------

        execution_status = "VALID"

        if action not in {
            "BUY",
            "STRONG BUY",
        }:
            execution_status = "NOT_ACTIONABLE"

        elif stop_loss >= entry_price:
            execution_status = "INVALID"

        elif target_1 <= entry_price:
            execution_status = "INVALID"

        elif position_size <= 0:
            execution_status = "INVALID"

        elif risk_reward < 1.5:
            execution_status = "WEAK_RISK_REWARD"

        return PortfolioExecutionSnapshot(
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            risk_per_share=round(
                risk_per_share,
                2,
            ),
            risk_reward=round(
                risk_reward,
                2,
            ),
            position_size=position_size,
            capital_required=round(
                capital_required,
                2,
            ),
            max_loss=round(
                actual_max_loss,
                2,
            ),
            execution_status=execution_status,
            confidence=confidence,
        )