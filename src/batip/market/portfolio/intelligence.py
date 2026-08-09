"""
BATIP Portfolio Intelligence.

Combines portfolio scoring, risk, and recommendation
into a single deterministic portfolio intelligence view.
"""

from dataclasses import dataclass
from typing import Any

from .scoring import PortfolioScoringEngine
from .risk import PortfolioRiskEngine
from .recommendation import PortfolioRecommendationEngine


@dataclass(frozen=True)
class PortfolioIntelligenceSnapshot:
    """Aggregated portfolio intelligence."""

    symbol: str
    score: int
    classification: str
    risk: str
    action: str
    confidence: float


class PortfolioIntelligenceEngine:
    """Aggregate portfolio scoring, risk, and recommendation."""

    def __init__(self) -> None:
        self.scoring_engine = PortfolioScoringEngine()
        self.risk_engine = PortfolioRiskEngine()
        self.recommendation_engine = PortfolioRecommendationEngine()

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from a dictionary or object."""

        if isinstance(data, dict):
            return data.get(field, default)

        return getattr(data, field, default)

    def analyze(
        self,
        holding: Any,
        *,
        market_bias: str | None = None,
        market_regime: str | None = None,
        breadth_score: int | None = None,
        sector_score: int | None = None,
    ) -> PortfolioIntelligenceSnapshot | None:
        """Generate a complete portfolio intelligence snapshot."""

        if holding is None:
            return None

        # ---------------------------------------------------------
        # Market context
        # ---------------------------------------------------------

        if market_bias is None:
            market_bias = str(
                self._value(holding, "market_bias", "Neutral")
            )

        if market_regime is None:
            market_regime = str(
                self._value(holding, "market_regime", "SIDEWAYS")
            )

        if breadth_score is None:
            breadth_score = int(
                self._value(holding, "breadth_score", 0)
            )

        if sector_score is None:
            sector_score = int(
                self._value(holding, "sector_score", 0)
            )

        # ---------------------------------------------------------
        # Portfolio scoring
        # ---------------------------------------------------------

        score = self.scoring_engine.analyze(holding)

        if score is None:
            return None

        # ---------------------------------------------------------
        # Portfolio risk
        # ---------------------------------------------------------

        risk = self.risk_engine.analyze(holding)

        if risk is None:
            return None

        # PortfolioRiskSnapshot exposes its risk_classification field.
        portfolio_risk = risk.risk_classification

        # ---------------------------------------------------------
        # Portfolio recommendation
        # ---------------------------------------------------------

        recommendation_input = {
            "symbol": score.symbol,
            "stock_score": score.score,
            "confidence": score.confidence,
            "market_bias": market_bias,
            "market_regime": market_regime,
            "breadth_score": breadth_score,
            "sector_score": sector_score,
            "portfolio_risk": portfolio_risk,
        }

        recommendation = self.recommendation_engine.analyze(
            recommendation_input
        )

        if recommendation is None:
            return None

        # ---------------------------------------------------------
        # Final intelligence snapshot
        # ---------------------------------------------------------

        return PortfolioIntelligenceSnapshot(
            symbol=score.symbol,
            score=score.score,
            classification=score.classification,
            risk=portfolio_risk,
            action=recommendation.action,
            confidence=score.confidence,
        )
