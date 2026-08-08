"""
BATIP Trade Manager.

Coordinates strategy validation, risk management, and prepared
paper-trading opportunities.

Paper trading only.
No broker connectivity.
No real order execution.
"""

from dataclasses import dataclass
from typing import Optional

from batip.trading.position import PaperPositionEngine, PaperPosition
from batip.trading.risk import RiskEngine


@dataclass
class ManagedTrade:
    """Represents a trade prepared by the trade manager."""

    symbol: str
    side: str
    direction: str
    quantity: int

    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float

    risk_amount: float
    risk_reward: float

    score: float = 0.0
    status: str = "PREPARED"


class TradeManager:
    """
    High-level paper-trading trade manager.

    Responsibilities:
    - validate trade direction
    - validate risk/reward
    - calculate position size
    - prepare paper trades
    - retrieve prepared trades
    - cancel prepared trades
    - open paper positions
    - update paper positions
    - close paper positions
    - expose portfolio P&L

    This class does not connect to a broker.
    """

    def __init__(
        self,
        capital: float = 100000.0,
        risk_percent: float = 1.0,
        minimum_risk_reward: float = 1.5,
    ) -> None:

        if capital <= 0:
            raise ValueError("Capital must be positive")

        if risk_percent <= 0:
            raise ValueError("Risk percent must be positive")

        if minimum_risk_reward <= 0:
            raise ValueError(
                "Minimum risk/reward must be positive"
            )

        self.capital = float(capital)
        self.risk_percent = float(risk_percent)
        self.minimum_risk_reward = float(minimum_risk_reward)

        self.position_engine = PaperPositionEngine()

        # Prepared trades are intentionally separate from
        # actual paper positions.
        self._trades: dict[str, ManagedTrade] = {}

    # ------------------------------------------------------------------
    # BASIC RISK
    # ------------------------------------------------------------------

    @property
    def maximum_risk(self) -> float:
        """Maximum monetary risk allowed per trade."""

        return RiskEngine.risk_amount(
            self.capital,
            self.risk_percent,
        )

    # ------------------------------------------------------------------
    # POSITION SIZE
    # ------------------------------------------------------------------

    def calculate_position_size(
        self,
        entry: float,
        stop_loss: float,
        capital: Optional[float] = None,
        risk_percent: Optional[float] = None,
    ) -> int:
        """
        Calculate maximum position size.

        Optional capital and risk_percent allow callers/tests to
        override the manager defaults for a single calculation.
        """

        effective_capital = (
            self.capital
            if capital is None
            else float(capital)
        )

        effective_risk_percent = (
            self.risk_percent
            if risk_percent is None
            else float(risk_percent)
        )

        return RiskEngine.position_size(
            effective_capital,
            effective_risk_percent,
            entry,
            stop_loss,
        )

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def validate_trade(
        self,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
    ) -> tuple[bool, str]:
        """
        Validate direction and risk/reward.

        Both validations must pass.
        """

        valid, reason = RiskEngine.validate_direction(
            direction,
            entry,
            stop_loss,
            target_1,
            target_2,
        )

        if not valid:
            return False, reason

        valid, reason = RiskEngine.validate_risk_reward(
            entry,
            stop_loss,
            target_1,
            self.minimum_risk_reward,
        )

        if not valid:
            return False, reason

        return (
            True,
            "Trade structure and risk/reward are valid",
        )

    # ------------------------------------------------------------------
    # PREPARE TRADE
    # ------------------------------------------------------------------

    def prepare_trade(
        self,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        score: float,
        capital: Optional[float] = None,
        risk_percent: Optional[float] = None,
    ) -> Optional[ManagedTrade]:
        """
        Validate and prepare a paper trade.

        A prepared trade is NOT an open position.

        Returns:
            ManagedTrade when valid.
            None when the setup fails validation.
        """

        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            return None

        # Validate price inputs before passing them into the
        # risk engine.
        if (
            entry <= 0
            or stop_loss <= 0
            or target_1 <= 0
            or target_2 <= 0
        ):
            return None

        valid, _reason = self.validate_trade(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
        )

        if not valid:
            return None

        # Prevent duplicate prepared trades.
        existing = self._trades.get(normalized_symbol)

        if existing is not None:
            if existing.status == "PREPARED":
                return None

        quantity = self.calculate_position_size(
            entry=entry,
            stop_loss=stop_loss,
            capital=capital,
            risk_percent=risk_percent,
        )

        if quantity <= 0:
            return None

        normalized_direction = direction.strip().lower()

        if normalized_direction in {
            "bullish",
            "long",
            "buy",
        }:
            side = "BUY"
            direction_name = "Bullish"

        elif normalized_direction in {
            "bearish",
            "short",
            "sell",
        }:
            side = "SELL"
            direction_name = "Bearish"

        else:
            return None

        effective_capital = (
            self.capital
            if capital is None
            else float(capital)
        )

        effective_risk_percent = (
            self.risk_percent
            if risk_percent is None
            else float(risk_percent)
        )

        risk_amount = (
            RiskEngine.risk_amount(
                effective_capital,
                effective_risk_percent,
            )
        )

        # Actual maximum loss for the calculated quantity.
        actual_risk = RiskEngine.maximum_loss(
            quantity,
            entry,
            stop_loss,
        )

        risk_reward = RiskEngine.risk_reward(
            entry,
            stop_loss,
            target_1,
        )

        # Use actual position risk rather than merely the configured
        # risk budget. This keeps the ManagedTrade accurate.
        if actual_risk > 0:
            risk_amount = actual_risk

        trade = ManagedTrade(
            symbol=normalized_symbol,
            side=side,
            direction=direction_name,
            quantity=quantity,
            entry_price=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            risk_amount=risk_amount,
            risk_reward=round(risk_reward, 2),
            score=score,
            status="PREPARED",
        )

        self._trades[normalized_symbol] = trade

        return trade

    # ------------------------------------------------------------------
    # TRADE LOOKUP
    # ------------------------------------------------------------------

    def get_trade(
        self,
        symbol: str,
    ) -> Optional[ManagedTrade]:
        """Return a prepared trade by symbol."""

        normalized_symbol = symbol.strip().upper()

        return self._trades.get(normalized_symbol)

    # ------------------------------------------------------------------
    # TRADE COUNT
    # ------------------------------------------------------------------

    def trade_count(self) -> int:
        """Return the number of prepared/managed trades."""

        return len(self._trades)

    # ------------------------------------------------------------------
    # CANCEL TRADE
    # ------------------------------------------------------------------

    def cancel_trade(
        self,
        symbol: str,
    ) -> bool:
        """
        Cancel a prepared trade.

        Returns:
            True when a prepared trade was cancelled.
            False when no cancellable trade exists.
        """

        normalized_symbol = symbol.strip().upper()

        trade = self._trades.get(normalized_symbol)

        if trade is None:
            return False

        if trade.status != "PREPARED":
            return False

        trade.status = "CANCELLED"

        return True

    # ------------------------------------------------------------------
    # OPEN PAPER TRADE
    # ------------------------------------------------------------------

    def open_trade(
        self,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        quantity: Optional[int] = None,
    ) -> ManagedTrade:
        """
        Open an actual paper position.

        This is separate from prepare_trade().
        """

        valid, reason = self.validate_trade(
            direction,
            entry,
            stop_loss,
            target_1,
            target_2,
        )

        if not valid:
            raise ValueError(reason)

        if quantity is None:
            quantity = self.calculate_position_size(
                entry,
                stop_loss,
            )

        if quantity <= 0:
            raise ValueError(
                "Calculated position size must be greater than zero"
            )

        position = self.position_engine.open_position(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            quantity=quantity,
        )

        risk_amount = RiskEngine.maximum_loss(
            quantity,
            entry,
            stop_loss,
        )

        risk_reward = RiskEngine.risk_reward(
            entry,
            stop_loss,
            target_1,
        )

        normalized_direction = direction.strip().lower()

        if normalized_direction in {
            "bullish",
            "long",
            "buy",
        }:
            side = "BUY"

        elif normalized_direction in {
            "bearish",
            "short",
            "sell",
        }:
            side = "SELL"

        else:
            raise ValueError(
                f"Unknown direction: {direction}"
            )

        normalized_symbol = symbol.strip().upper()

        trade = ManagedTrade(
            symbol=normalized_symbol,
            side=side,
            direction=position.direction,
            quantity=position.quantity,
            entry_price=position.entry,
            stop_loss=position.stop_loss,
            target_1=position.target_1,
            target_2=position.target_2,
            risk_amount=risk_amount,
            risk_reward=round(risk_reward, 2),
            status=position.status,
        )

        self._trades[normalized_symbol] = trade

        return trade

    # ------------------------------------------------------------------
    # POSITION MANAGEMENT
    # ------------------------------------------------------------------

    def update_price(
        self,
        symbol: str,
        price: float,
    ) -> PaperPosition:
        """Update market price for a paper position."""

        return self.position_engine.update_price(
            symbol,
            price,
        )

    def close_trade(
        self,
        symbol: str,
        price: float,
        reason: str = "MANUAL",
    ) -> float:
        """Close a paper trade."""

        pnl = self.position_engine.close_position(
            symbol,
            price,
            reason=reason,
        )

        normalized_symbol = symbol.strip().upper()

        managed_trade = self._trades.get(normalized_symbol)

        if managed_trade is not None:
            managed_trade.status = "CLOSED"

        return pnl

    # ------------------------------------------------------------------
    # POSITIONS
    # ------------------------------------------------------------------

    def get_position(
        self,
        symbol: str,
    ) -> PaperPosition:
        """Return a paper position."""

        return self.position_engine.get_position(symbol)

    def all_positions(self) -> list[PaperPosition]:
        """Return all paper positions."""

        return self.position_engine.all_positions()

    def open_positions(self) -> list[PaperPosition]:
        """Return currently open paper positions."""

        return self.position_engine.open_positions()

    def closed_positions(self) -> list[PaperPosition]:
        """Return closed paper positions."""

        return self.position_engine.closed_positions()

    # ------------------------------------------------------------------
    # P&L
    # ------------------------------------------------------------------

    def total_realized_pnl(self) -> float:
        """Return total realized P&L."""

        return self.position_engine.total_realized_pnl()

    def total_unrealized_pnl(self) -> float:
        """Return total unrealized P&L."""

        return self.position_engine.total_unrealized_pnl()

    def total_pnl(self) -> float:
        """Return total P&L."""

        return self.position_engine.total_pnl()

    # ------------------------------------------------------------------
    # CLEANUP
    # ------------------------------------------------------------------

    def remove_closed_position(
        self,
        symbol: str,
    ) -> Optional[PaperPosition]:
        """Remove a closed paper position."""

        return self.position_engine.remove_closed_position(
            symbol
        )