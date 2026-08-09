"""
BATIP Portfolio Recommendation Intelligence.

Combines stock intelligence, market conditions, sector strength,
breadth, and portfolio risk into a deterministic action.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioRecommendationSnapshot:
    """Final portfolio recommendation."""

    symbol: str
    action: str
    confidence: float


class PortfolioRecommendationEngine:
    """Generate deterministic portfolio actions."""

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
    ) -> PortfolioRecommendationSnapshot | None:
        """Generate a portfolio recommendation."""

        if data is None:
            return None

        symbol = str(self._value(data, "symbol", ""))

        stock_score = int(self._value(data, "stock_score", 0))
        confidence = float(self._value(data, "confidence", 0))

        market_bias = str(self._value(data, "market_bias", "Neutral")).upper()
        market_regime = str(self._value(data, "market_regime", "SIDEWAYS")).upper()
        breadth_score = int(self._value(data, "breadth_score", 0))
        sector_score = int(self._value(data, "sector_score", 0))
        portfolio_risk = str(self._value(data, "portfolio_risk", "LOW")).upper()

        # ---------------------------------------------------------
        # Start with the stock signal.
        # ---------------------------------------------------------
        score = stock_score

        # ---------------------------------------------------------
        # Market environment adjustment.
        # ---------------------------------------------------------
        if market_bias == "BULLISH":
            score += 1
        elif market_bias == "BEARISH":
            score -= 2

        # ---------------------------------------------------------
        # Market regime adjustment.
        # ---------------------------------------------------------
        if market_regime == "BULL":
            score += 1
        elif market_regime == "BEAR":
            score -= 2

        # ---------------------------------------------------------
        # Breadth adjustment.
        # ---------------------------------------------------------
        if breadth_score >= 2:
            score += 1
        elif breadth_score <= -2:
            score -= 1

        # ---------------------------------------------------------
        # Sector strength adjustment.
        # ---------------------------------------------------------
        if sector_score >= 2:
            score += 1
        elif sector_score <= -2:
            score -= 1

        # ---------------------------------------------------------
        # Base recommendation (updated thresholds).
        # ---------------------------------------------------------
        if score >= 12 and confidence >= 90:
            action = "STRONG BUY"
        elif score >= 6 and confidence >= 70:
            action = "BUY"
        elif score >= 2 and confidence >= 60:
            action = "HOLD"
        elif score >= 0:
            action = "WATCH"
        elif score >= -8:
            action = "REDUCE"
        else:
            action = "EXIT"

        # ---------------------------------------------------------
        # Risk overrides.
        # ---------------------------------------------------------
        if portfolio_risk == "HIGH":
            if action in {"STRONG BUY", "BUY"}:
                action = "HOLD"

        # ---------------------------------------------------------
        # Bear-market overrides.
        # ---------------------------------------------------------
        if (
            market_bias == "BEARISH"
            and market_regime == "BEAR"
            and stock_score > 0
        ):
            if action in {"STRONG BUY", "BUY"}:
                action = "HOLD"

        return PortfolioRecommendationSnapshot(
            symbol=symbol,
            action=action,
            confidence=confidence,
        )
