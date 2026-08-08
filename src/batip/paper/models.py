"""
BATIP Paper Trading Models
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    TARGET_1 = "TARGET_1"
    TARGET_2 = "TARGET_2"
    STOPPED = "STOPPED"
    CLOSED = "CLOSED"


@dataclass(slots=True)
class PaperTrade:
    symbol: str
    side: PositionSide

    entry: float
    stop_loss: float
    target_1: float
    target_2: float

    quantity: int = 1

    status: TradeStatus = TradeStatus.OPEN

    current_price: float | None = None
    exit_price: float | None = None

    pnl: float = 0.0
    pnl_percent: float = 0.0

    created_at: datetime | None = None
    closed_at: datetime | None = None

    exit_reason: str | None = None

    def update_price(self, price: float) -> None:
        self.current_price = price

        if self.side == PositionSide.LONG:
            self.pnl = (price - self.entry) * self.quantity
        else:
            self.pnl = (self.entry - price) * self.quantity

        if self.entry != 0:
            self.pnl_percent = (
                self.pnl / (self.entry * self.quantity)
            ) * 100