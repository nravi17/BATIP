"""
BATIP Portfolio Decision Pipeline.

Orchestrates portfolio intelligence, recommendation, decision,
allocation, and execution into one deterministic pipeline.
"""

from dataclasses import dataclass
from typing import Any

from .snapshot import PortfolioSnapshotEngine
from .scoring import PortfolioScoringEngine, PortfolioScoreSnapshot
from .risk import PortfolioRiskEngine
from .recommendation import PortfolioRecommendationEngine
from .decision import PortfolioDecisionEngine
from .allocation import PortfolioAllocationEngine
from .execution import PortfolioExecutionEngine


@dataclass(frozen=True)
class PortfolioPipelineSnapshot:
    """Final end-to-end portfolio pipeline result."""

    symbol: str
    score: int
    classification: str
    risk: str
    recommendation: str
    decision: str
    allocation: Any
    execution: Any
    confidence: float


class PortfolioPipelineEngine:
    """Orchestrate the complete portfolio decision pipeline."""

    def __init__(self) -> None:
        self.snapshot_engine = PortfolioSnapshotEngine()
        self.scoring_engine = PortfolioScoringEngine()
        self.risk_engine = PortfolioRiskEngine()
        self.recommendation_engine = PortfolioRecommendationEngine()
        self.decision_engine = PortfolioDecisionEngine()
        self.allocation_engine = PortfolioAllocationEngine()
        self.execution_engine = PortfolioExecutionEngine()

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = None,
    ) -> Any:
        """Safely extract a value from a dict or object."""

        if isinstance(data, dict):
            return data.get(field, default)

        return getattr(data, field, default)

    def analyze(
        self,
        holding: Any,
    ) -> PortfolioPipelineSnapshot | None:
        """Run the complete portfolio intelligence pipeline."""

        if holding is None:
            return None

        # --- Normalize input contract ---
        pipeline_input = dict(holding) if isinstance(holding, dict) else holding

        if isinstance(pipeline_input, dict):
            if "score" not in pipeline_input and "stock_score" in pipeline_input:
                pipeline_input["score"] = pipeline_input["stock_score"]

            if "risk" not in pipeline_input and "portfolio_risk" in pipeline_input:
                pipeline_input["risk"] = pipeline_input["portfolio_risk"]

        snapshot = self.snapshot_engine.analyze(pipeline_input)

        if snapshot is None:
            return None

        # --- Portfolio scoring ---
        stock_score = self._value(
            pipeline_input,
            "stock_score",
            None,
        )

        if stock_score is not None:
            score_value = int(stock_score)

            score_input = {
                "symbol": self._value(pipeline_input, "symbol", ""),
                "strength_score": 0,
                "momentum_score": 0,
                "volume_score": 0,
                "signal_score": 0,
                "confidence": float(
                    self._value(pipeline_input, "confidence", 0)
                ),
            }

            base_score = self.scoring_engine.analyze(score_input)

            if base_score is None:
                return None

            score = PortfolioScoreSnapshot(
                symbol=base_score.symbol,
                score=score_value,
                classification=self.scoring_engine.classify(score_value),
                confidence=base_score.confidence,
            )
        else:
            score = self.scoring_engine.analyze(pipeline_input)

            if score is None:
                return None

        risk = self.risk_engine.analyze(pipeline_input)

        if risk is None:
            return None

        market_bias = str(
            self._value(pipeline_input, "market_bias", "Neutral")
        )

        market_regime = str(
            self._value(pipeline_input, "market_regime", "SIDEWAYS")
        )

        breadth_score = int(
            self._value(pipeline_input, "breadth_score", 0)
        )

        sector_score = int(
            self._value(pipeline_input, "sector_score", 0)
        )

        # --- Resolve portfolio risk ---
        #
        # If upstream portfolio intelligence already supplied an explicit
        # portfolio risk classification, preserve it. Otherwise use the
        # calculated risk engine classification.
        provided_risk = self._value(
            pipeline_input,
            "portfolio_risk",
            None,
        )

        if provided_risk is not None:
            portfolio_risk = str(provided_risk).upper()
        else:
            portfolio_risk = risk.risk_classification

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

        recommendation_result = self.recommendation_engine.analyze(
            recommendation_input
        )

        if recommendation_result is None:
            return None

        # --- Normalize WATCH → HOLD at pipeline level ---
        recommendation = recommendation_result.action
        if recommendation == "WATCH":
            recommendation = "HOLD"

        decision_input = {
            "symbol": score.symbol,
            "action": recommendation,
            "score": score.score,
            "risk": portfolio_risk,
            "confidence": score.confidence,
        }

        decision = self.decision_engine.analyze(
            decision_input
        )

        if decision is None:
            return None

        # --- Final portfolio risk protection ---
        # HIGH portfolio risk must never result in BUY/STRONG BUY.
        final_decision = decision.action
        if portfolio_risk.upper() == "HIGH" and final_decision in {
            "BUY",
            "STRONG BUY",
        }:
            final_decision = "HOLD"

        allocation_input = {
            "symbol": score.symbol,
            "action": final_decision,
            "score": score.score,
            "risk": portfolio_risk,
            "confidence": score.confidence,
        }

        allocation = self.allocation_engine.analyze(
            allocation_input
        )

        if allocation is None:
            return None

        execution_input = {
            "symbol": score.symbol,
            "action": final_decision,
            "score": score.score,
            "risk": portfolio_risk,
            "confidence": score.confidence,
        }

        execution = self.execution_engine.analyze(
            execution_input
        )

        if execution is None:
            return None

        return PortfolioPipelineSnapshot(
            symbol=score.symbol,
            score=score.score,
            classification=score.classification,
            risk=portfolio_risk,
            recommendation=recommendation,
            decision=final_decision,
            allocation=allocation,
            execution=execution,
            confidence=score.confidence,
        )
