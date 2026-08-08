"""
BATIP Signal -> Paper Trading Bridge

Connects BATIP signals to the paper trading engine.

Signal mapping:
    STRONG_BUY -> LONG
    BUY        -> LONG
    WAIT       -> No trade
    SELL       -> SHORT
    STRONG_SELL -> SHORT

Duplicate active signals are ignored.
Signal reversals close the existing position.
"""

from batip.paper.engine import PaperTradingEngine
from batip.paper.models import PaperTrade, PositionSide
from batip.analytics.signal import Signal


class SignalBridge:
    """
    Converts BATIP signals into paper trades.
    """

    def __init__(self, engine: PaperTradingEngine) -> None:
        self.engine = engine
        self._last_signal: dict[str, str] = {}

    @staticmethod
    def _normalize_signal(signal: Signal | str) -> str:
        value = (
            signal.value
            if isinstance(signal, Signal)
            else str(signal)
        )

        value = value.upper()

        # Handle enum string representations such as
        # Signal.STRONG_SELL if necessary.
        if "." in value:
            value = value.split(".")[-1]

        return value

    @staticmethod
    def _position_side(signal_value: str) -> PositionSide:
        if signal_value in ("BUY", "STRONG_BUY"):
            return PositionSide.LONG

        if signal_value in ("SELL", "STRONG_SELL"):
            return PositionSide.SHORT

        raise ValueError(
            f"Unsupported BATIP signal: {signal_value}"
        )

    def process(
        self,
        symbol: str,
        signal: Signal | str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        quantity: int = 1,
    ) -> PaperTrade | None:

        signal_value = self._normalize_signal(signal)

        # WAIT means no new trade.
        if signal_value == "WAIT":
            self._last_signal[symbol] = "WAIT"
            return None

        if signal_value not in (
            "BUY",
            "STRONG_BUY",
            "SELL",
            "STRONG_SELL",
        ):
            raise ValueError(
                f"Unsupported BATIP signal: {signal_value}"
            )

        new_side = self._position_side(signal_value)

        # --------------------------------------------------
        # Duplicate active signal
        # --------------------------------------------------

        if self._last_signal.get(symbol) == signal_value:

            open_trades = [
                trade
                for trade in self.engine.open_trades()
                if trade.symbol == symbol
            ]

            if open_trades:
                return open_trades[-1]

        # --------------------------------------------------
        # Check existing position
        # --------------------------------------------------

        existing = [
            trade
            for trade in self.engine.open_trades()
            if trade.symbol == symbol
        ]

        if existing:

            current = existing[-1]

            # Same direction:
            # keep existing position.
            if current.side == new_side:
                self._last_signal[symbol] = signal_value
                return current

            # Opposite direction:
            # close existing position.
            self.engine.close_trade(
                current,
                entry,
                reason="Signal Reversal",
            )

        # --------------------------------------------------
        # Open new position
        # --------------------------------------------------

        trade = self.engine.open_trade(
            symbol=symbol,
            side=new_side,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            quantity=quantity,
        )

        self._last_signal[symbol] = signal_value

        return trade