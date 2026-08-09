"""
BATIP Trading Orchestrator.

Connects the existing paper-trading components into one workflow.

Flow:

Decision Engine
    -> Portfolio Allocation
    -> Trade Manager
    -> Paper Execution

No broker connectivity.
No real-money order execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from batip.trading.decision import TradeDecision, TradeDecisionEngine
from batip.trading.execution import ExecutionEngine, Order
from batip.trading.portfolio import (
    PortfolioAllocation,
    PortfolioAllocator,
)
from batip.trading.trade_manager import TradeManager


@dataclass(slots=True)
class OrchestratedTrade:
    """Result of preparing one paper trade."""

    decision: TradeDecision
    candidate: dict[str, Any] | None = None
    order: Order | None = None
    allocated: bool = False
    reason: str = ""


@dataclass(slots=True)
class PortfolioRun:
    """Result of processing multiple trading candidates."""

    decisions: list[TradeDecision]
    allocation: PortfolioAllocation
    orders: list[Order]


class TradingOrchestrator:
    """
    Coordinate BATIP's existing paper-trading components.

    This class does not replace the individual engines.
    It only connects them.
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
        self.capital = float(capital)
        self.risk_percent = float(risk_percent)

        self.decision_engine = TradeDecisionEngine(
            capital=capital,
            risk_percent=risk_percent,
            minimum_risk_reward=minimum_risk_reward,
        )

        self.portfolio_allocator = PortfolioAllocator(
            capital=capital,
            max_portfolio_risk_percent=max_portfolio_risk_percent,
            max_positions=max_positions,
        )

        self.trade_manager = TradeManager(
            capital=capital,
            risk_percent=risk_percent,
            minimum_risk_reward=minimum_risk_reward,
        )

        self.execution_engine = ExecutionEngine()

    def evaluate(
        self,
        *,
        symbol: str,
        stock_score: int,
        technical_score: int,
        market_score: int,
        sector_score: int,
        entry: float | None = None,
        stop_loss: float | None = None,
        target_1: float | None = None,
        target_2: float | None = None,
    ) -> TradeDecision:
        """Evaluate one symbol using the existing decision engine."""

        return self.decision_engine.evaluate(
            symbol=symbol,
            stock_score=stock_score,
            technical_score=technical_score,
            market_score=market_score,
            sector_score=sector_score,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
        )

    def build_candidate(
        self,
        decision: TradeDecision,
    ) -> dict[str, Any] | None:
        """
        Convert a valid TRADE decision into a portfolio candidate.

        WATCH and AVOID decisions are intentionally excluded.
        """

        if decision.trade_action != "TRADE":
            return None

        setup = decision.setup

        if setup is None or not setup.valid:
            return None

        position_size = getattr(setup, "position_size", 0)

        maximum_loss = getattr(setup, "maximum_loss", 0.0)

        entry = getattr(setup, "entry", 0.0)

        if position_size <= 0:
            return None

        if entry <= 0:
            return None

        if maximum_loss <= 0:
            return None

        return {
            "symbol": decision.symbol.strip().upper(),
            "action": decision.trade_action,
            "score": decision.opportunity_score,
            "direction": decision.direction,
            "entry": entry,
            "stop_loss": getattr(setup, "stop_loss", 0.0),
            "target_1": getattr(setup, "target_1", 0.0),
            "target_2": getattr(setup, "target_2", 0.0),
            "position_size": position_size,
            "maximum_loss": maximum_loss,
            "confidence": decision.confidence,
            "intraday": decision.intraday,
            "overnight": decision.overnight,
        }

    def allocate(
        self,
        decisions: list[TradeDecision],
    ) -> PortfolioAllocation:
        """Allocate all valid TRADE decisions."""

        candidates = []

        for decision in decisions:
            candidate = self.build_candidate(decision)

            if candidate is not None:
                candidates.append(candidate)

        return self.portfolio_allocator.allocate(candidates)

    def prepare_trade(
        self,
        decision: TradeDecision,
    ) -> OrchestratedTrade:
        """
        Prepare one decision for paper execution.

        The trade must pass:
        1. decision validation
        2. candidate validation
        3. trade-manager preparation
        4. paper-order validation
        """

        if decision.trade_action != "TRADE":
            return OrchestratedTrade(
                decision=decision,
                reason=(
                    f"Decision action is "
                    f"{decision.trade_action}; "
                    f"paper trade not authorized"
                ),
            )

        candidate = self.build_candidate(decision)

        if candidate is None:
            return OrchestratedTrade(
                decision=decision,
                reason="Decision does not contain a valid trade candidate",
            )

        setup = decision.setup

        if setup is None:
            return OrchestratedTrade(
                decision=decision,
                candidate=candidate,
                reason="Trade setup is missing",
            )

        direction = decision.direction.strip().lower()

        if direction in {"bullish", "long", "buy"}:
            side = "BUY"
        elif direction in {"bearish", "short", "sell"}:
            side = "SELL"
        else:
            return OrchestratedTrade(
                decision=decision,
                candidate=candidate,
                reason=f"Unknown trade direction: {decision.direction}",
            )

        order = self.execution_engine.create_order(
            symbol=candidate["symbol"],
            side=side,
            quantity=candidate["position_size"],
            entry=candidate["entry"],
            stop_loss=candidate["stop_loss"],
            target_1=candidate["target_1"],
            target_2=candidate["target_2"],
        )

        if order.status == "REJECTED":
            return OrchestratedTrade(
                decision=decision,
                candidate=candidate,
                order=order,
                reason=order.reason,
            )

        return OrchestratedTrade(
            decision=decision,
            candidate=candidate,
            order=order,
            allocated=True,
            reason="Paper trade prepared successfully",
        )

    def run(
        self,
        decisions: list[TradeDecision],
    ) -> PortfolioRun:
        """
        Allocate and prepare all eligible paper trades.

        Only allocated candidates are sent to execution.
        """

        allocation = self.allocate(decisions)

        allocated_symbols = {
            str(candidate.get("symbol", "")).strip().upper()
            for candidate in allocation.positions
        }

        orders: list[Order] = []

        for decision in decisions:
            symbol = decision.symbol.strip().upper()

            if symbol not in allocated_symbols:
                continue

            result = self.prepare_trade(decision)

            if result.order is not None:
                if result.order.status != "REJECTED":
                    orders.append(result.order)

        return PortfolioRun(
            decisions=decisions,
            allocation=allocation,
            orders=orders,
        )

    def fill_order(
        self,
        order_id: str,
        fill_price: float,
    ) -> Order | None:
        """Fill a paper order."""

        if fill_price <= 0:
            raise ValueError("Fill price must be positive")

        return self.execution_engine.fill_order(
            order_id,
            fill_price,
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> Order | None:
        """Cancel a pending paper order."""

        return self.execution_engine.cancel_order(order_id)

    def get_order(
        self,
        order_id: str,
    ) -> Order | None:
        """Return a paper order by ID."""

        return self.execution_engine.get_order(order_id)

    def open_orders(self) -> list[Order]:
        """Return currently active paper orders."""

        return [
            order
            for order in self.execution_engine.orders.values()
            if order.status in {"PENDING", "FILLED"}
        ]

    def rejected_orders(self) -> list[Order]:
        """Return rejected paper orders."""

        return [
            order
            for order in self.execution_engine.orders.values()
            if order.status == "REJECTED"
        ]