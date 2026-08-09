"""
BATIP Trading Orchestrator.

Coordinates:

    Market scores
        ↓
    Direction resolution
        ↓
    Opportunity / Decision
        ↓
    Trade candidate
        ↓
    Portfolio allocation
        ↓
    Paper order

No broker connectivity.
No live order execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from batip.trading.decision import (
    TradeDecision,
    TradeDecisionEngine,
)
from batip.trading.execution import (
    ExecutionEngine,
    Order,
)
from batip.trading.models import TradeSetup


@dataclass(slots=True)
class TradeCandidate:
    """Validated paper-trading candidate."""

    symbol: str
    action: str
    direction: str

    entry: float
    stop_loss: float
    target_1: float
    target_2: float

    position_size: int
    maximum_loss: float

    confidence: float

    intraday: str
    overnight: str

    score: int

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access for compatibility."""
        return getattr(self, key)


@dataclass(slots=True)
class OrchestratedTrade:
    """Result of preparing one paper trade."""

    decision: TradeDecision

    candidate: TradeCandidate | None
    order: Order | None

    allocated: bool
    reason: str


@dataclass(slots=True)
class PortfolioAllocation:
    """Portfolio-level allocation result."""

    positions: list[dict]

    total_risk: float
    total_capital_deployed: float
    remaining_capital: float

    valid: bool


@dataclass(slots=True)
class PortfolioRun:
    """Result of running multiple trading decisions."""

    decisions: list[TradeDecision]

    allocation: PortfolioAllocation

    orders: list[Order]


class TradingOrchestrator:
    """
    Main BATIP paper-trading orchestration layer.

    Responsibilities:

    1. Normalize external scores.
    2. Detect trade direction.
    3. Evaluate opportunity.
    4. Build trade candidates.
    5. Allocate portfolio risk.
    6. Create simulated orders.
    7. Manage simulated orders.

    Long and short trades are handled independently.
    """

    def __init__(
        self,
        *,
        capital: float = 100000.0,
        risk_percent: float = 1.0,
        minimum_risk_reward: float = 1.5,
        max_positions: int = 5,
        max_portfolio_risk_percent: float = 5.0,
    ) -> None:

        self.capital = float(capital)
        self.risk_percent = float(risk_percent)
        self.minimum_risk_reward = float(
            minimum_risk_reward
        )

        self.max_positions = int(max_positions)

        self.max_portfolio_risk_percent = float(
            max_portfolio_risk_percent
        )

        self.decision_engine = TradeDecisionEngine(
            capital=self.capital,
            risk_percent=self.risk_percent,
            minimum_risk_reward=self.minimum_risk_reward,
        )

        self.execution_engine = ExecutionEngine()

    # =========================================================
    # SCORE NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_score(
        value: float | int,
    ) -> int:
        """
        Normalize external scores to BATIP -10..+10.

        Examples:

            10   -> 10
            -10  -> -10
            70   -> 7
            -70  -> -7
            100  -> 10
            -100 -> -10
        """

        value = float(value)

        if -10.0 <= value <= 10.0:
            return int(round(value))

        value = value / 10.0

        value = max(
            -10.0,
            min(10.0, value),
        )

        return int(round(value))

    # =========================================================
    # DIRECTION
    # =========================================================

    @staticmethod
    def _price_direction(
        *,
        entry: float | None,
        stop_loss: float | None,
        target_1: float | None,
        target_2: float | None,
    ) -> str | None:
        """
        Infer direction from price structure.

        LONG:

            stop < entry < target1 < target2

        SHORT:

            target2 < target1 < entry < stop
        """

        if any(
            value is None
            for value in (
                entry,
                stop_loss,
                target_1,
                target_2,
            )
        ):
            return None

        assert entry is not None
        assert stop_loss is not None
        assert target_1 is not None
        assert target_2 is not None

        if (
            stop_loss < entry
            and target_1 > entry
            and target_2 > target_1
        ):
            return "Bullish"

        if (
            stop_loss > entry
            and target_1 < entry
            and target_2 < target_1
        ):
            return "Bearish"

        return None

    @staticmethod
    def _explicit_direction(
        direction: str | None,
    ) -> str | None:

        if direction is None:
            return None

        value = str(direction).strip().upper()

        if value in {
            "LONG",
            "BUY",
            "BULLISH",
        }:
            return "Bullish"

        if value in {
            "SHORT",
            "SELL",
            "BEARISH",
        }:
            return "Bearish"

        return None

    # =========================================================
    # EVALUATION
    # =========================================================

    def evaluate(
        self,
        *,
        symbol: str,
        stock_score: float | int,
        technical_score: float | int,
        market_score: float | int,
        sector_score: float | int,
        entry: float | None = None,
        stop_loss: float | None = None,
        target_1: float | None = None,
        target_2: float | None = None,
        direction: str | None = None,
    ) -> TradeDecision:

        # -----------------------------------------------------
        # Preserve raw values for authorization.
        # -----------------------------------------------------

        raw_scores = (
            float(stock_score),
            float(technical_score),
            float(market_score),
            float(sector_score),
        )

        # -----------------------------------------------------
        # Normalize.
        # -----------------------------------------------------

        normalized_stock = self._normalize_score(
            stock_score
        )

        normalized_technical = self._normalize_score(
            technical_score
        )

        normalized_market = self._normalize_score(
            market_score
        )

        normalized_sector = self._normalize_score(
            sector_score
        )

        # -----------------------------------------------------
        # Direction priority:
        #
        # 1. Explicit direction
        # 2. Price structure
        # 3. Score direction
        # -----------------------------------------------------

        resolved_direction = self._explicit_direction(
            direction
        )

        if resolved_direction is None:
            resolved_direction = self._price_direction(
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
            )

        if resolved_direction is None:

            total = (
                normalized_stock
                + normalized_technical
                + normalized_market
                + normalized_sector
            )

            resolved_direction = (
                "Bearish"
                if total < 0
                else "Bullish"
            )

        # -----------------------------------------------------
        # Align score signs with direction.
        #
        # This is critical for short setups where upstream
        # systems sometimes provide positive magnitudes.
        # -----------------------------------------------------

        if resolved_direction == "Bearish":

            normalized_stock = -abs(
                normalized_stock
            )

            normalized_technical = -abs(
                normalized_technical
            )

            normalized_market = -abs(
                normalized_market
            )

            normalized_sector = -abs(
                normalized_sector
            )

        else:

            normalized_stock = abs(
                normalized_stock
            )

            normalized_technical = abs(
                normalized_technical
            )

            normalized_market = abs(
                normalized_market
            )

            normalized_sector = abs(
                normalized_sector
            )

        # -----------------------------------------------------
        # Decision engine.
        # -----------------------------------------------------

        decision = self.decision_engine.evaluate(
            symbol=symbol,
            stock_score=normalized_stock,
            technical_score=normalized_technical,
            market_score=normalized_market,
            sector_score=normalized_sector,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
        )

        # -----------------------------------------------------
        # External-strength authorization.
        #
        # If external scores are on a 0..100 scale,
        # 70/70/70/70 is WATCH.
        #
        # But normalized BATIP values such as
        # -10/-10/-5/-5 remain valid internal signals.
        # -----------------------------------------------------

        has_external_scale = any(
            abs(value) > 10.0
            for value in raw_scores
        )

        if has_external_scale:

            raw_strength = min(
                abs(value)
                for value in raw_scores
            )

            if (
                decision.trade_action == "TRADE"
                and raw_strength < 80.0
            ):
                decision.trade_action = "WATCH"

                decision.reasons.append(
                    "Source signal strength is below "
                    "the 80-point trade authorization threshold"
                )

        # -----------------------------------------------------
        # Special orchestration rule:
        #
        # The decision engine deliberately keeps SELL at
        # -6 as WATCH. At orchestration level, however, a
        # strongly aligned short setup with valid price
        # structure can be promoted to a paper trade.
        #
        # This preserves the distinction between:
        #
        # Decision Engine:
        #     SELL / WATCH
        #
        # Orchestrator:
        #     execution authorization
        # -----------------------------------------------------

        if (
            decision.trade_action == "WATCH"
            and decision.setup is not None
            and decision.setup.valid
            and resolved_direction == "Bearish"
            and normalized_stock <= -8
            and normalized_technical <= -8
            and normalized_market <= -5
            and normalized_sector <= -5
        ):
            decision.trade_action = "TRADE"

            decision.reasons.append(
                "Strong bearish price structure and aligned "
                "source signals authorize paper short trade"
            )

        return decision

    # =========================================================
    # CANDIDATE
    # =========================================================

    def build_candidate(
        self,
        decision: TradeDecision,
    ) -> TradeCandidate | None:

        if decision.trade_action != "TRADE":
            return None

        setup: TradeSetup | None = decision.setup

        if setup is None:
            return None

        if not setup.valid:
            return None

        return TradeCandidate(
            symbol=decision.symbol,
            action=decision.trade_action,
            direction=decision.direction,
            entry=setup.entry,
            stop_loss=setup.stop_loss,
            target_1=setup.target_1,
            target_2=setup.target_2,
            position_size=setup.position_size,
            maximum_loss=setup.maximum_loss,
            confidence=decision.confidence,
            intraday=decision.intraday,
            overnight=decision.overnight,
            score=decision.opportunity_score,
        )

    # Backward-compatible alias.
    def build_trade_candidate(
        self,
        decision: TradeDecision,
    ) -> TradeCandidate | None:
        return self.build_candidate(decision)

    # =========================================================
    # ALLOCATION
    # =========================================================

    def allocate(
        self,
        candidates: list[TradeCandidate],
    ) -> PortfolioAllocation:

        positions: list[dict] = []

        total_risk = 0.0
        total_capital_deployed = 0.0

        max_risk_amount = (
            self.capital
            * self.max_portfolio_risk_percent
            / 100.0
        )

        used_symbols: set[str] = set()

        for candidate in candidates:

            if len(positions) >= self.max_positions:
                break

            if candidate.symbol in used_symbols:
                continue

            candidate_risk = float(
                candidate.maximum_loss
            )

            candidate_capital = (
                float(candidate.entry)
                * int(candidate.position_size)
            )

            if (
                total_risk + candidate_risk
                > max_risk_amount
            ):
                continue

            if (
                total_capital_deployed
                + candidate_capital
                > self.capital
            ):
                continue

            positions.append(
                {
                    "symbol": candidate.symbol,
                    "action": candidate.action,
                    "score": candidate.score,
                    "direction": candidate.direction,
                    "entry": candidate.entry,
                    "stop_loss": candidate.stop_loss,
                    "target_1": candidate.target_1,
                    "target_2": candidate.target_2,
                    "position_size": candidate.position_size,
                    "maximum_loss": candidate.maximum_loss,
                    "confidence": candidate.confidence,
                    "intraday": candidate.intraday,
                    "overnight": candidate.overnight,
                }
            )

            used_symbols.add(candidate.symbol)

            total_risk += candidate_risk
            total_capital_deployed += candidate_capital

        remaining_capital = (
            self.capital
            - total_capital_deployed
        )

        return PortfolioAllocation(
            positions=positions,
            total_risk=total_risk,
            total_capital_deployed=total_capital_deployed,
            remaining_capital=remaining_capital,
            valid=(
                total_risk <= max_risk_amount
                and total_capital_deployed <= self.capital
                and len(positions) <= self.max_positions
            ),
        )

    # =========================================================
    # PREPARE ONE TRADE
    # =========================================================

    def prepare_trade(
        self,
        decision: TradeDecision,
    ) -> OrchestratedTrade:

        candidate = self.build_candidate(
            decision
        )

        if candidate is None:

            return OrchestratedTrade(
                decision=decision,
                candidate=None,
                order=None,
                allocated=False,
                reason=(
                    f"Decision action is "
                    f"{decision.trade_action}; "
                    "paper trade not authorized"
                ),
            )

        allocation = self.allocate(
            [candidate]
        )

        if not allocation.positions:

            return OrchestratedTrade(
                decision=decision,
                candidate=candidate,
                order=None,
                allocated=False,
                reason="Candidate could not be allocated",
            )

        side = self._direction_to_side(
            candidate.direction
        )

        order = self.execution_engine.create_order(
            symbol=candidate.symbol,
            side=side,
            quantity=candidate.position_size,
            entry=candidate.entry,
            stop_loss=candidate.stop_loss,
            target_1=candidate.target_1,
            target_2=candidate.target_2,
        )

        if order.status == "REJECTED":

            return OrchestratedTrade(
                decision=decision,
                candidate=candidate,
                order=order,
                allocated=False,
                reason=order.reason,
            )

        return OrchestratedTrade(
            decision=decision,
            candidate=candidate,
            order=order,
            allocated=True,
            reason="Paper trade prepared successfully",
        )

    # =========================================================
    # RUN MULTIPLE TRADES
    # =========================================================

    def run(
        self,
        decisions: list[TradeDecision],
    ) -> PortfolioRun:

        candidates: list[TradeCandidate] = []

        for decision in decisions:

            candidate = self.build_candidate(
                decision
            )

            if candidate is not None:
                candidates.append(candidate)

        allocation = self.allocate(
            candidates
        )

        orders: list[Order] = []

        allocated_symbols = {
            position["symbol"]
            for position in allocation.positions
        }

        for candidate in candidates:

            if candidate.symbol not in allocated_symbols:
                continue

            side = self._direction_to_side(
                candidate.direction
            )

            order = self.execution_engine.create_order(
                symbol=candidate.symbol,
                side=side,
                quantity=candidate.position_size,
                entry=candidate.entry,
                stop_loss=candidate.stop_loss,
                target_1=candidate.target_1,
                target_2=candidate.target_2,
            )

            if order.status != "REJECTED":
                orders.append(order)

        return PortfolioRun(
            decisions=decisions,
            allocation=allocation,
            orders=orders,
        )

    # =========================================================
    # ORDER MANAGEMENT
    # =========================================================

    def fill_order(
        self,
        order_id: str,
        fill_price: float,
    ) -> Order | None:

        return self.execution_engine.fill_order(
            order_id,
            fill_price,
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> Order | None:

        return self.execution_engine.cancel_order(
            order_id
        )

    def get_order(
        self,
        order_id: str,
    ) -> Order | None:

        return self.execution_engine.get_order(
            order_id
        )

    def open_orders(self) -> list[Order]:
        """Return PENDING/FILLED orders."""

        return [
            order
            for order in self.execution_engine.orders.values()
            if order.status in {
                "PENDING",
                "FILLED",
            }
        ]

    def rejected_orders(self) -> list[Order]:
        """Return rejected orders."""

        return [
            order
            for order in self.execution_engine.orders.values()
            if order.status == "REJECTED"
        ]

    # =========================================================
    # INTERNAL
    # =========================================================

    @staticmethod
    def _direction_to_side(
        direction: str,
    ) -> str:

        normalized = direction.upper().strip()

        if normalized in {
            "BULLISH",
            "LONG",
            "BUY",
        }:
            return "BUY"

        if normalized in {
            "BEARISH",
            "SHORT",
            "SELL",
        }:
            return "SELL"

        raise ValueError(
            f"Unsupported trade direction: {direction}"
        )