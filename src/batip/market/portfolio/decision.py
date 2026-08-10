"""
BATIP Portfolio Decision Intelligence.

Converts complete portfolio intelligence into a final
deterministic portfolio decision.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioDecisionSnapshot:
    """Final portfolio decision."""

    symbol: str
    decision: str
    confidence: float


class PortfolioDecisionEngine:
    """Generate deterministic portfolio decisions."""

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

    @staticmethod
    def _decision(
        action: str,
        risk: str,
    ) -> str:
        """Apply portfolio risk overrides to the recommendation."""

        action = action.upper()
        risk = risk.upper()

        if risk == "HIGH":
            if action in {"STRONG BUY", "BUY"}:
                return "HOLD"

        return action

    def analyze(
        self,
        data: Any,
    ) -> PortfolioDecisionSnapshot | None:
        """Generate a final portfolio decision."""

        if data is None:
            return None

        symbol = str(
            self._value(data, "symbol", "")
        )

        action = str(
            self._value(data, "action", "WATCH")
        ).upper()

        risk = str(
            self._value(data, "risk", "LOW")
        ).upper()

        confidence = float(
            self._value(data, "confidence", 0)
        )

        decision = self._decision(
            action,
            risk,
        )

        return PortfolioDecisionSnapshot(
            symbol=symbol,
            decision=decision,
            confidence=confidence,
        )
