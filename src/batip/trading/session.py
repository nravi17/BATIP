"""
BATIP Trading Session Manager.

Coordinates:
    TradingOrchestrator
    PaperTradingEngine
    Paper orders
    Paper trades

No broker connectivity.
No real-money execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from batip.paper.engine import PaperTradingEngine
from batip.paper.models import PaperTrade
from batip.trading.execution import Order
from batip.trading.orchestrator import (
    OrchestratedTrade,
    PortfolioRun,
    TradingOrchestrator,
)


@dataclass(slots=True)
class SessionSummary:
    """Current summary of a trading session."""

    session_id: str
    status: str

    started_at: datetime | None
    closed_at: datetime | None

    total_orders: int
    pending_orders: int
    filled_orders: int
    cancelled_orders: int
    rejected_orders: int

    open_trades: int
    closed_trades: int

    total_pnl: float


@dataclass(slots=True)
class TradingSession:
    """Internal session representation."""

    session_id: str

    status: str = "CREATED"

    started_at: datetime | None = None
    closed_at: datetime | None = None

    orders: list[Order] = field(
        default_factory=list
    )


class TradingSessionManager:
    """Manage one BATIP paper-trading session."""

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
            max_portfolio_risk_percent=(
                max_portfolio_risk_percent
            ),
            max_positions=max_positions,
        )

        self.paper_engine = PaperTradingEngine()

        self.session: TradingSession | None = None

    # =========================================================
    # Session lifecycle
    # =========================================================

    def start(
        self,
        session_id: str = "default",
    ) -> TradingSession:

        if (
            self.session is not None
            and self.session.status == "ACTIVE"
        ):
            raise RuntimeError(
                "A trading session is already active"
            )

        self.session = TradingSession(
            session_id=session_id,
            status="ACTIVE",
            started_at=datetime.now(),
        )

        return self.session

    def close(self) -> TradingSession:

        session = self._require_session()

        if session.status == "CLOSED":
            return session

        session.status = "CLOSED"
        session.closed_at = datetime.now()

        return session

    def _require_session(self) -> TradingSession:

        if self.session is None:
            raise RuntimeError(
                "No trading session has been started"
            )

        if self.session.status != "ACTIVE":
            raise RuntimeError(
                "Trading session is not active"
            )

        return self.session

    @property
    def is_active(self) -> bool:

        return (
            self.session is not None
            and self.session.status == "ACTIVE"
        )

    def _require_active_session(self) -> None:

        if not self.is_active:
            raise RuntimeError(
                "Trading session is not active"
            )

    # =========================================================
    # Trading workflow
    # =========================================================

    def run(
        self,
        decisions: list[Any],
    ) -> PortfolioRun:

        session = self._require_session()

        result = self.orchestrator.run(
            decisions
        )

        for order in result.orders:
            session.orders.append(order)

        return result

    def prepare_trade(
        self,
        decision: Any,
    ) -> OrchestratedTrade:

        session = self._require_session()

        result = self.orchestrator.prepare_trade(
            decision
        )

        if result.order is not None:
            session.orders.append(
                result.order
            )

        return result

    # =========================================================
    # Orders
    # =========================================================

    def fill_order(
        self,
        order_id: str,
        fill_price: float,
    ) -> Order | None:

        self._require_session()

        order = self.orchestrator.fill_order(
            order_id,
            fill_price,
        )

        if order is None:
            return None

        if order.status != "FILLED":
            return order

        self._create_paper_trade(order)

        return order

    def cancel_order(
        self,
        order_id: str,
    ) -> Order | None:

        self._require_session()

        return self.orchestrator.cancel_order(
            order_id
        )

    def get_order(
        self,
        order_id: str,
    ) -> Order | None:

        self._require_session()

        return self.orchestrator.get_order(
            order_id
        )

    def open_orders(self) -> list[Order]:

        self._require_session()

        return self.orchestrator.open_orders()

    def rejected_orders(self) -> list[Order]:

        self._require_session()

        return self.orchestrator.rejected_orders()

    # =========================================================
    # Paper trades
    # =========================================================

    def _create_paper_trade(
        self,
        order: Order,
    ) -> PaperTrade:

        from batip.paper.models import PositionSide

        side = order.side.upper()

        if side == "BUY":
            position_side = PositionSide.LONG

        elif side == "SELL":
            position_side = PositionSide.SHORT

        else:
            raise ValueError(
                f"Unsupported order side: {order.side}"
            )

        return self.paper_engine.open_trade(
            symbol=order.symbol,
            side=position_side,
            entry=(
                order.fill_price
                if order.fill_price is not None
                else order.entry
            ),
            stop_loss=order.stop_loss,
            target_1=order.target_1,
            target_2=order.target_2,
            quantity=order.quantity,
        )

    def update_trade(
        self,
        trade: PaperTrade,
        price: float,
    ) -> PaperTrade:

        self._require_session()

        return self.paper_engine.update_trade(
            trade,
            price,
        )

    def close_trade(
        self,
        trade: PaperTrade,
        price: float,
        reason: str = "Manual Close",
    ) -> PaperTrade:

        self._require_session()

        return self.paper_engine.close_trade(
            trade,
            price,
            reason,
        )

    def open_trades(self) -> list[PaperTrade]:

        self._require_session()

        return self.paper_engine.open_trades()

    def closed_trades(self) -> list[PaperTrade]:

        self._require_session()

        return self.paper_engine.closed_trades()

    def total_pnl(self) -> float:

        self._require_session()

        return self.paper_engine.total_pnl()

    # =========================================================
    # Summary
    # =========================================================

    def summary(self) -> SessionSummary:

        if self.session is None:

            return SessionSummary(
                session_id="",
                status="NOT_STARTED",
                started_at=None,
                closed_at=None,
                total_orders=0,
                pending_orders=0,
                filled_orders=0,
                cancelled_orders=0,
                rejected_orders=0,
                open_trades=0,
                closed_trades=0,
                total_pnl=0.0,
            )

        orders = self.session.orders

        pending_orders = sum(
            1
            for order in orders
            if order.status == "PENDING"
        )

        filled_orders = sum(
            1
            for order in orders
            if order.status == "FILLED"
        )

        cancelled_orders = sum(
            1
            for order in orders
            if order.status == "CANCELLED"
        )

        rejected_orders = sum(
            1
            for order in orders
            if order.status == "REJECTED"
        )

        return SessionSummary(
            session_id=self.session.session_id,
            status=self.session.status,
            started_at=self.session.started_at,
            closed_at=self.session.closed_at,
            total_orders=len(orders),
            pending_orders=pending_orders,
            filled_orders=filled_orders,
            cancelled_orders=cancelled_orders,
            rejected_orders=rejected_orders,
            open_trades=len(
                self.paper_engine.open_trades()
            ),
            closed_trades=len(
                self.paper_engine.closed_trades()
            ),
            total_pnl=self.paper_engine.total_pnl(),
        )