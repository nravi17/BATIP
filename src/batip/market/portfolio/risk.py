"""
BATIP Portfolio Risk Intelligence Engine.

Calculates deterministic portfolio-level risk using
position concentration, sector concentration, volatility,
and drawdown.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioRiskSnapshot:
    """Portfolio-level risk snapshot."""

    risk_score: int
    risk_classification: str

    concentration_risk: bool
    sector_concentration_risk: bool
    dominant_sector: str | None

    max_position_weight: float
    average_volatility: float
    max_drawdown: float

    holding_count: int


class PortfolioRiskEngine:
    """Analyze portfolio-level risk."""

    @staticmethod
    def _value(
        holding: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from a dict or object."""

        if isinstance(holding, dict):
            return holding.get(field, default)

        return getattr(holding, field, default)

    @staticmethod
    def classify(risk_score: int) -> str:
        """Classify overall portfolio risk."""

        if risk_score >= 60:
            return "HIGH"

        if risk_score >= 30:
            return "MODERATE"

        return "LOW"

    def analyze(
        self,
        holdings: list[Any],
    ) -> PortfolioRiskSnapshot:
        """Calculate deterministic portfolio risk."""

        valid_holdings = [
            holding for holding in holdings
            if holding is not None
        ]

        holding_count = len(valid_holdings)

        if not valid_holdings:
            return PortfolioRiskSnapshot(
                risk_score=0,
                risk_classification="LOW",
                concentration_risk=False,
                sector_concentration_risk=False,
                dominant_sector=None,
                max_position_weight=0.0,
                average_volatility=0.0,
                max_drawdown=0.0,
                holding_count=0,
            )

        weights = [
            float(self._value(holding, "weight", 0))
            for holding in valid_holdings
        ]

        volatilities = [
            float(self._value(holding, "volatility", 0))
            for holding in valid_holdings
        ]

        drawdowns = [
            float(self._value(holding, "drawdown", 0))
            for holding in valid_holdings
        ]

        max_position_weight = max(weights)
        average_volatility = sum(volatilities) / holding_count
        max_drawdown = min(drawdowns)

        # Position concentration.
        concentration_risk = max_position_weight > 50.0

        # Sector concentration.
        sector_weights: dict[str, float] = {}

        for holding in valid_holdings:
            sector = str(self._value(holding, "sector", "UNKNOWN"))
            weight = float(self._value(holding, "weight", 0))
            sector_weights[sector] = (
                sector_weights.get(sector, 0.0) + weight
            )

        dominant_sector = None

        if sector_weights:
            dominant_sector = max(
                sector_weights,
                key=sector_weights.get,
            )

        dominant_sector_weight = (
            sector_weights.get(dominant_sector, 0.0)
            if dominant_sector is not None
            else 0.0
        )

        sector_concentration_risk = (
            dominant_sector_weight > 50.0
        )

        # ---------------------------------------------------------
        # Risk scoring
        # ---------------------------------------------------------
        risk_score = 0

        # Position concentration: 0–30 points.
        if max_position_weight > 50:
            risk_score += 30
        elif max_position_weight > 35:
            risk_score += 20
        elif max_position_weight > 25:
            risk_score += 10

        # Sector concentration: 0–25 points.
        if dominant_sector_weight > 60:
            risk_score += 25
        elif dominant_sector_weight > 50:
            risk_score += 20
        elif dominant_sector_weight > 40:
            risk_score += 10

        # Volatility: 0–25 points.
        if average_volatility >= 35:
            risk_score += 25
        elif average_volatility >= 25:
            risk_score += 15
        elif average_volatility >= 20:
            risk_score += 10

        # Drawdown: 0–20 points.
        if max_drawdown <= -25:
            risk_score += 20
        elif max_drawdown <= -15:
            risk_score += 15
        elif max_drawdown <= -10:
            risk_score += 10
        elif max_drawdown < -5:
            risk_score += 5

        return PortfolioRiskSnapshot(
            risk_score=risk_score,
            risk_classification=self.classify(risk_score),
            concentration_risk=concentration_risk,
            sector_concentration_risk=sector_concentration_risk,
            dominant_sector=dominant_sector,
            max_position_weight=max_position_weight,
            average_volatility=average_volatility,
            max_drawdown=max_drawdown,
            holding_count=holding_count,
        )