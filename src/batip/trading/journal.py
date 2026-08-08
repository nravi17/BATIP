from dataclasses import dataclass, asdict
from typing import List, Optional
from uuid import uuid4


@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str
    quantity: int
    entry_price: float
    exit_price: float
    stop_loss: float
    target_1: float
    target_2: float
    exit_reason: str
    pnl: float
    result: str

    def to_dict(self) -> dict:
        return asdict(self)


class TradeJournal:
    """
    Records completed paper trades and provides basic trading statistics.

    Supported sides:
        BUY  -> profit when exit_price > entry_price
        SELL -> profit when exit_price < entry_price
    """

    def __init__(self):
        self._trades: List[TradeRecord] = []

    @property
    def trades(self) -> List[TradeRecord]:
        """Return all recorded trades."""
        return list(self._trades)

    @property
    def trade_count(self) -> int:
        """Return the total number of recorded trades."""
        return len(self._trades)

    @property
    def total_pnl(self) -> float:
        """Return total P&L across all trades."""
        return round(sum(trade.pnl for trade in self._trades), 2)

    @property
    def winning_trades(self) -> int:
        """Return number of profitable trades."""
        return sum(1 for trade in self._trades if trade.result == "WIN")

    @property
    def losing_trades(self) -> int:
        """Return number of losing trades."""
        return sum(1 for trade in self._trades if trade.result == "LOSS")

    @property
    def win_rate(self) -> float:
        """
        Return winning-trade percentage rounded to two decimals.

        Example:
            2 wins / 3 trades = 66.67%
        """
        if self.trade_count == 0:
            return 0.0

        return round((self.winning_trades / self.trade_count) * 100, 2)

    @property
    def gross_profit(self) -> float:
        """Return total profit from winning trades."""
        return round(
            sum(trade.pnl for trade in self._trades if trade.pnl > 0),
            2,
        )

    @property
    def gross_loss(self) -> float:
        """Return total absolute loss from losing trades."""
        return round(
            sum(abs(trade.pnl) for trade in self._trades if trade.pnl < 0),
            2,
        )

    @property
    def profit_factor(self) -> float:
        """
        Return gross profit / gross loss.

        If there are no losses:
            - 0 trades -> 0.0
            - profitable trades only -> infinity
        """
        if self.gross_loss == 0:
            if self.gross_profit > 0:
                return float("inf")
            return 0.0

        return round(self.gross_profit / self.gross_loss, 2)

    def record_trade(
        self,
        symbol: str,
        side: str,
        quantity: int,
        entry_price: float,
        exit_price: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        exit_reason: str,
    ) -> TradeRecord:
        """
        Record a completed trade.

        Parameters:
            symbol:
                Stock symbol, e.g. RELIANCE.

            side:
                BUY for long trades.
                SELL for short trades.

            quantity:
                Number of shares.

            entry_price:
                Trade entry price.

            exit_price:
                Trade exit price.

            stop_loss:
                Stop-loss level.

            target_1:
                First target.

            target_2:
                Second target.

            exit_reason:
                Reason for closing the trade, e.g.
                TARGET_1, TARGET_2, STOP_LOSS, MANUAL.
        """

        symbol = str(symbol).upper().strip()
        side = str(side).upper().strip()
        exit_reason = str(exit_reason).upper().strip()

        if not symbol:
            raise ValueError("symbol cannot be empty")

        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")

        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if entry_price <= 0:
            raise ValueError("entry_price must be greater than zero")

        if exit_price <= 0:
            raise ValueError("exit_price must be greater than zero")

        if stop_loss <= 0:
            raise ValueError("stop_loss must be greater than zero")

        if target_1 <= 0:
            raise ValueError("target_1 must be greater than zero")

        if target_2 <= 0:
            raise ValueError("target_2 must be greater than zero")

        # BUY = long position
        # SELL = short position
        if side == "BUY":
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity

        pnl = round(pnl, 2)

        if pnl > 0:
            result = "WIN"
        elif pnl < 0:
            result = "LOSS"
        else:
            result = "BREAKEVEN"

        trade = TradeRecord(
            trade_id=str(uuid4()),
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            exit_price=exit_price,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            exit_reason=exit_reason,
            pnl=pnl,
            result=result,
        )

        self._trades.append(trade)

        return trade

    def get_trade(self, trade_id: str) -> Optional[TradeRecord]:
        """Return a trade by its trade_id."""
        for trade in self._trades:
            if trade.trade_id == trade_id:
                return trade

        return None

    def get_trades_by_symbol(self, symbol: str) -> List[TradeRecord]:
        """Return all trades for a particular symbol."""
        symbol = str(symbol).upper().strip()

        return [
            trade
            for trade in self._trades
            if trade.symbol == symbol
        ]

    def clear(self) -> None:
        """Remove all recorded trades."""
        self._trades.clear()

    def summary(self) -> dict:
        """Return a compact journal performance summary."""
        return {
            "trade_count": self.trade_count,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_pnl": self.total_pnl,
            "win_rate": self.win_rate,
            "gross_profit": self.gross_profit,
            "gross_loss": self.gross_loss,
            "profit_factor": self.profit_factor,
        }