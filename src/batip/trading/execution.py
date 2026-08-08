from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class Order:
    order_id: str
    symbol: str
    side: str
    quantity: int
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    status: str = "PENDING"
    fill_price: Optional[float] = None
    reason: str = ""


class ExecutionEngine:
    """
    Paper-trading order execution engine.

    This module does not connect to a broker.
    It only creates and manages simulated orders.
    """

    def __init__(self):
        self.orders = {}

    def create_order(
        self,
        symbol,
        side,
        quantity,
        entry,
        stop_loss,
        target_1,
        target_2,
    ):
        side = side.upper()

        # Basic validation
        if side not in ("BUY", "SELL"):
            return self._rejected_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                reason="Invalid order side",
            )

        if quantity <= 0:
            return self._rejected_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                reason="Quantity must be greater than zero",
            )

        # Validate price structure
        if side == "BUY":
            valid_levels = (
                stop_loss < entry
                and target_1 > entry
                and target_2 > target_1
            )
        else:
            valid_levels = (
                stop_loss > entry
                and target_1 < entry
                and target_2 < target_1
            )

        if not valid_levels:
            return self._rejected_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                reason="Invalid price levels",
            )

        # Prevent duplicate active orders for same symbol.
        for existing in self.orders.values():
            if (
                existing.symbol == symbol
                and existing.status in ("PENDING", "FILLED")
            ):
                return self._rejected_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    entry=entry,
                    stop_loss=stop_loss,
                    target_1=target_1,
                    target_2=target_2,
                    reason="Active order already exists for symbol",
                )

        order = Order(
            order_id=str(uuid4()),
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
        )

        self.orders[order.order_id] = order

        return order

    def fill_order(self, order_id, fill_price):
        order = self.orders.get(order_id)

        if order is None:
            return None

        if order.status != "PENDING":
            return order

        order.status = "FILLED"
        order.fill_price = fill_price

        return order

    def cancel_order(self, order_id):
        order = self.orders.get(order_id)

        if order is None:
            return None

        if order.status == "PENDING":
            order.status = "CANCELLED"

        return order

    def get_order(self, order_id):
        return self.orders.get(order_id)

    def _rejected_order(
        self,
        symbol,
        side,
        quantity,
        entry,
        stop_loss,
        target_1,
        target_2,
        reason,
    ):
        order = Order(
            order_id=str(uuid4()),
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            status="REJECTED",
            reason=reason,
        )

        return order