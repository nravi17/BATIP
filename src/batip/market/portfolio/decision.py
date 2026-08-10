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
    action: str
    score: int
    risk: str
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

        score = int(
            self._value(data, "score", 0)
        )

        # --- Decision Flow ---
        final_action = action

        # High-risk protection
        if risk == "HIGH" and final_action in {"BUY", "STRONG BUY"}:
            final_action = "HOLD"

        # Low-confidence protection
        if confidence < 60 and final_action in {"BUY", "STRONG BUY"}:
            final_action = "HOLD"

        return PortfolioDecisionSnapshot(
            symbol=symbol,
            action=final_action,
            score=score,
            risk=risk,
            confidence=confidence,
        )
