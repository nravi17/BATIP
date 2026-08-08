"""
BATIP Paper Trading Engine
"""

from datetime import datetime

from batip.paper.models import (
    PaperTrade,
    PositionSide,
    TradeStatus,
)


class PaperTradingEngine:
    """
    Simulates trade execution without placing real broker orders.
    """

    def __init__(self) -> None:
        self.trades: list[PaperTrade] = []

    def open_trade(
        self,
        symbol: str,
        side: PositionSide,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        quantity: int = 1,
    ) -> PaperTrade:

        trade = PaperTrade(
            symbol=symbol,
            side=side,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            quantity=quantity,
            created_at=datetime.now(),
        )

        self.trades.append(trade)

        return trade

    def update_trade(
        self,
        trade: PaperTrade,
        price: float,
    ) -> PaperTrade:

        if trade.status not in (
            TradeStatus.OPEN,
            TradeStatus.TARGET_1,
        ):
            return trade

        trade.update_price(price)

        if trade.side == PositionSide.LONG:

            if price <= trade.stop_loss:
                self._close(
                    trade,
                    price,
                    TradeStatus.STOPPED,
                    "Stop Loss",
                )

            elif price >= trade.target_2:
                self._close(
                    trade,
                    price,
                    TradeStatus.TARGET_2,
                    "Target 2",
                )

            elif (
                price >= trade.target_1
                and trade.status == TradeStatus.OPEN
            ):
                trade.status = TradeStatus.TARGET_1

        else:

            if price >= trade.stop_loss:
                self._close(
                    trade,
                    price,
                    TradeStatus.STOPPED,
                    "Stop Loss",
                )

            elif price <= trade.target_2:
                self._close(
                    trade,
                    price,
                    TradeStatus.TARGET_2,
                    "Target 2",
                )

            elif (
                price <= trade.target_1
                and trade.status == TradeStatus.OPEN
            ):
                trade.status = TradeStatus.TARGET_1

        return trade

    @staticmethod
    def _close(
        trade: PaperTrade,
        price: float,
        status: TradeStatus,
        reason: str,
    ) -> None:

        trade.update_price(price)

        trade.exit_price = price
        trade.status = status
        trade.exit_reason = reason
        trade.closed_at = datetime.now()

    def close_trade(
        self,
        trade: PaperTrade,
        price: float,
        reason: str = "Manual Close",
    ) -> PaperTrade:

        trade.update_price(price)

        trade.exit_price = price
        trade.status = TradeStatus.CLOSED
        trade.exit_reason = reason
        trade.closed_at = datetime.now()

        return trade

    def open_trades(self) -> list[PaperTrade]:
        return [
            trade
            for trade in self.trades
            if trade.status
            in (
                TradeStatus.OPEN,
                TradeStatus.TARGET_1,
            )
        ]

    def closed_trades(self) -> list[PaperTrade]:
        return [
            trade
            for trade in self.trades
            if trade.status
            not in (
                TradeStatus.OPEN,
                TradeStatus.TARGET_1,
            )
        ]

    def total_pnl(self) -> float:
        return sum(
            trade.pnl
            for trade in self.trades
        )