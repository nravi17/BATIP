"""
BATIP Paper Trading Position Engine.

Tracks paper-trading positions only.

No broker connectivity.
No real order execution.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PaperPosition:
    """Represents one paper-trading position."""

    symbol: str
    direction: str
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    quantity: int

    current_price: float = 0.0
    status: str = "OPEN"

    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0

    target_1_hit: bool = False
    target_2_hit: bool = False
    stop_loss_hit: bool = False

    @property
    def capital_deployed(self) -> float:
        """Capital deployed for the position."""
        return self.entry * self.quantity

    @property
    def maximum_loss(self) -> float:
        """Maximum loss if stop loss is hit."""
        return abs(self.entry - self.stop_loss) * self.quantity

    def update_price(self, price: float) -> None:
        """Update market price and unrealized P&L."""

        if price <= 0:
            raise ValueError("Price must be positive")

        self.current_price = price

        if self.status != "OPEN":
            return

        direction = self.direction.strip().lower()

        if direction in {"bullish", "long", "buy"}:
            self.unrealized_pnl = (
                price - self.entry
            ) * self.quantity

        elif direction in {"bearish", "short", "sell"}:
            self.unrealized_pnl = (
                self.entry - price
            ) * self.quantity

        else:
            raise ValueError(
                f"Unknown direction: {self.direction}"
            )

        self._check_levels(price)

    def _check_levels(self, price: float) -> None:
        """Check stop loss and target levels."""

        direction = self.direction.strip().lower()

        if direction in {"bullish", "long", "buy"}:
            if price <= self.stop_loss:
                self.close(
                    self.stop_loss,
                    reason="STOP_LOSS",
                )
                self.stop_loss_hit = True
                return

            if price >= self.target_2:
                self.target_1_hit = True
                self.target_2_hit = True
                self.close(
                    self.target_2,
                    reason="TARGET_2",
                )
                return

            if price >= self.target_1:
                self.target_1_hit = True

        elif direction in {"bearish", "short", "sell"}:
            if price >= self.stop_loss:
                self.close(
                    self.stop_loss,
                    reason="STOP_LOSS",
                )
                self.stop_loss_hit = True
                return

            if price <= self.target_2:
                self.target_1_hit = True
                self.target_2_hit = True
                self.close(
                    self.target_2,
                    reason="TARGET_2",
                )
                return

            if price <= self.target_1:
                self.target_1_hit = True

    def close(
        self,
        price: float,
        reason: str = "MANUAL",
    ) -> float:
        """Close the paper position."""

        if price <= 0:
            raise ValueError("Close price must be positive")

        if self.status == "CLOSED":
            return self.realized_pnl

        direction = self.direction.strip().lower()

        if direction in {"bullish", "long", "buy"}:
            pnl = (
                price - self.entry
            ) * self.quantity

        elif direction in {"bearish", "short", "sell"}:
            pnl = (
                self.entry - price
            ) * self.quantity

        else:
            raise ValueError(
                f"Unknown direction: {self.direction}"
            )

        self.current_price = price
        self.realized_pnl = pnl
        self.unrealized_pnl = 0.0
        self.status = "CLOSED"

        if reason == "STOP_LOSS":
            self.stop_loss_hit = True

        elif reason == "TARGET_1":
            self.target_1_hit = True

        elif reason == "TARGET_2":
            self.target_1_hit = True
            self.target_2_hit = True

        return pnl


class PaperPositionEngine:
    """Create and manage paper-trading positions."""

    def __init__(self) -> None:
        self._positions: dict[str, PaperPosition] = {}

    def open_position(
        self,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        quantity: int,
    ) -> PaperPosition:
        """Open a new paper position."""

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError("Symbol is required")

        if entry <= 0:
            raise ValueError("Entry must be positive")

        if stop_loss <= 0:
            raise ValueError("Stop loss must be positive")

        if target_1 <= 0:
            raise ValueError("Target 1 must be positive")

        if target_2 <= 0:
            raise ValueError("Target 2 must be positive")

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        direction_normalized = direction.strip().lower()

        if direction_normalized in {
            "bullish",
            "long",
            "buy",
        }:
            direction_name = "Bullish"

        elif direction_normalized in {
            "bearish",
            "short",
            "sell",
        }:
            direction_name = "Bearish"

        else:
            raise ValueError(
                f"Unknown direction: {direction}"
            )

        if symbol in self._positions:
            existing = self._positions[symbol]

            if existing.status == "OPEN":
                raise ValueError(
                    f"Open position already exists for {symbol}"
                )

        position = PaperPosition(
            symbol=symbol,
            direction=direction_name,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            quantity=quantity,
            current_price=entry,
        )

        self._positions[symbol] = position

        return position

    def update_price(
        self,
        symbol: str,
        price: float,
    ) -> PaperPosition:
        """Update the price of an existing position."""

        symbol = symbol.strip().upper()

        position = self.get_position(symbol)

        position.update_price(price)

        return position

    def close_position(
        self,
        symbol: str,
        price: float,
        reason: str = "MANUAL",
    ) -> float:
        """Close an existing paper position."""

        position = self.get_position(symbol)

        return position.close(
            price,
            reason=reason,
        )

    def get_position(
        self,
        symbol: str,
    ) -> PaperPosition:
        """Return a position by symbol."""

        symbol = symbol.strip().upper()

        if symbol not in self._positions:
            raise KeyError(
                f"No position found for {symbol}"
            )

        return self._positions[symbol]

    def all_positions(self) -> list[PaperPosition]:
        """Return all paper positions."""
        return list(self._positions.values())

    def open_positions(self) -> list[PaperPosition]:
        """Return currently open positions."""

        return [
            position
            for position in self._positions.values()
            if position.status == "OPEN"
        ]

    def closed_positions(self) -> list[PaperPosition]:
        """Return closed positions."""

        return [
            position
            for position in self._positions.values()
            if position.status == "CLOSED"
        ]

    def total_realized_pnl(self) -> float:
        """Return total realized P&L."""

        return sum(
            position.realized_pnl
            for position in self._positions.values()
        )

    def total_unrealized_pnl(self) -> float:
        """Return total unrealized P&L."""

        return sum(
            position.unrealized_pnl
            for position in self._positions.values()
            if position.status == "OPEN"
        )

    def total_pnl(self) -> float:
        """Return realized plus unrealized P&L."""

        return (
            self.total_realized_pnl()
            + self.total_unrealized_pnl()
        )

    def remove_closed_position(
        self,
        symbol: str,
    ) -> Optional[PaperPosition]:
        """Remove a closed position from the engine."""

        symbol = symbol.strip().upper()

        position = self._positions.get(symbol)

        if position is None:
            return None

        if position.status != "CLOSED":
            raise ValueError(
                f"Position for {symbol} is still open"
            )

        return self._positions.pop(symbol)


class PositionManager(PaperPositionEngine):
    """
    Compatibility facade for TradeManager.

    PositionManager intentionally inherits the existing
    PaperPositionEngine so the existing position functionality
    remains unchanged while TradeManager can use the expected
    PositionManager name.
    """

    pass