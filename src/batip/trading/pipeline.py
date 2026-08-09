"""
BATIP Trading Pipeline.

Connects the market decision, portfolio allocation,
trade orchestration and paper-trading workflow.

Flow:

Market Inputs
    ↓
Decision Engine
    ↓
Portfolio Allocation
    ↓
Trading Orchestrator
    ↓
Paper Orders

No broker connectivity.
No real-money execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from batip.trading.decision import TradeDecision
from batip.trading.execution import Order
from batip.trading.orchestrator import (
    OrchestratedTrade,
    PortfolioRun,
    TradingOrchestrator,
)


@dataclass(slots=True)
class PipelineInput:
    """Market inputs required to evaluate one symbol."""

    symbol: str

    stock_score: int
    technical_score: int
    market_score: int
    sector_score: int

    entry: float | None = None
    stop_loss: float | None = None
    target_1: float | None = None
    target_2: float | None = None


@dataclass(slots=True)
class PipelineResult:
    """Result of processing one or more market inputs."""

    decisions: list[TradeDecision]
    run: PortfolioRun
    orders: list[Order]


class TradingPipeline:
    """
    High-level BATIP trading workflow.

    This class is intentionally thin. The individual engines remain
    responsible for their own business rules.
    """

    def __init__(
        self,
        *,
        capital: float = 100000.0,
        risk_percent: float = 1.0,
        minimum_risk_reward: float = 1.5,
        max_portfolio_risk_percent: float = 3.0,
        max_positions: int = 3,
    ) -> None:

        self.orchestrator = TradingOrchestrator(
            capital=capital,
            risk_percent=risk_percent,
            minimum_risk_reward=minimum_risk_reward,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            max_positions=max_positions,
        )

    def evaluate(
        self,
        market_input: PipelineInput,
    ) -> TradeDecision:
        """Evaluate one market input."""

        return self.orchestrator.evaluate(
            symbol=market_input.symbol,
            stock_score=market_input.stock_score,
            technical_score=market_input.technical_score,
            market_score=market_input.market_score,
            sector_score=market_input.sector_score,
            entry=market_input.entry,
            stop_loss=market_input.stop_loss,
            target_1=market_input.target_1,
            target_2=market_input.target_2,
        )

    def evaluate_many(
        self,
        inputs: list[PipelineInput],
    ) -> list[TradeDecision]:
        """Evaluate multiple market inputs."""

        return [
            self.evaluate(market_input)
            for market_input in inputs
        ]

    def prepare(
        self,
        market_input: PipelineInput,
    ) -> OrchestratedTrade:
        """Evaluate and prepare one paper trade."""

        decision = self.evaluate(market_input)

        return self.orchestrator.prepare_trade(
            decision
        )

    def run(
        self,
        inputs: list[PipelineInput],
    ) -> PipelineResult:
        """
        Evaluate all inputs and run the eligible trades
        through portfolio allocation and paper execution.
        """

        decisions = self.evaluate_many(inputs)

        run_result = self.orchestrator.run(
            decisions
        )

        return PipelineResult(
            decisions=decisions,
            run=run_result,
            orders=run_result.orders,
        )

    def fill_order(
        self,
        order_id: str,
        fill_price: float,
    ) -> Order | None:
        """Fill a pending paper order."""

        return self.orchestrator.fill_order(
            order_id,
            fill_price,
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> Order | None:
        """Cancel a pending paper order."""

        return self.orchestrator.cancel_order(
            order_id
        )

    def get_order(
        self,
        order_id: str,
    ) -> Order | None:
        """Return an order by ID."""

        return self.orchestrator.get_order(
            order_id
        )

    def open_orders(self) -> list[Order]:
        """Return currently active paper orders."""

        return self.orchestrator.open_orders()

    def rejected_orders(self) -> list[Order]:
        """Return rejected paper orders."""

        return self.orchestrator.rejected_orders()

    def summary(
        self,
        result: PipelineResult,
    ) -> dict[str, Any]:
        """Return a compact pipeline summary."""

        trade_count = sum(
            1
            for decision in result.decisions
            if decision.trade_action == "TRADE"
        )

        watch_count = sum(
            1
            for decision in result.decisions
            if decision.trade_action == "WATCH"
        )

        avoid_count = sum(
            1
            for decision in result.decisions
            if decision.trade_action == "AVOID"
        )

        return {
            "total_inputs": len(result.decisions),
            "trade_decisions": trade_count,
            "watch_decisions": watch_count,
            "avoid_decisions": avoid_count,
            "allocated_positions": len(
                result.run.allocation.positions
            ),
            "orders_created": len(result.orders),
            "allocation_valid": (
                result.run.allocation.valid
            ),
        }