from batip.paper.engine import PaperTradingEngine
from batip.paper.models import PositionSide
from batip.paper.signal_bridge import SignalBridge


def test_strong_buy_creates_long_trade():

    engine = PaperTradingEngine()
    bridge = SignalBridge(engine)

    trade = bridge.process(
        symbol="NIFTY",
        signal="STRONG_BUY",
        entry=24500,
        stop_loss=24300,
        target_1=24700,
        target_2=24900,
    )

    assert trade is not None
    assert trade.side == PositionSide.LONG
    assert trade.entry == 24500


def test_strong_sell_creates_short_trade():

    engine = PaperTradingEngine()
    bridge = SignalBridge(engine)

    trade = bridge.process(
        symbol="NIFTY",
        signal="STRONG_SELL",
        entry=24500,
        stop_loss=24700,
        target_1=24300,
        target_2=24100,
    )

    assert trade is not None
    assert trade.side == PositionSide.SHORT
    assert trade.entry == 24500


def test_wait_creates_no_trade():

    engine = PaperTradingEngine()
    bridge = SignalBridge(engine)

    trade = bridge.process(
        symbol="NIFTY",
        signal="WAIT",
        entry=24500,
        stop_loss=24300,
        target_1=24700,
        target_2=24900,
    )

    assert trade is None
    assert len(engine.trades) == 0


def test_signal_reversal_closes_existing_trade():

    engine = PaperTradingEngine()
    bridge = SignalBridge(engine)

    long_trade = bridge.process(
        symbol="NIFTY",
        signal="BUY",
        entry=24500,
        stop_loss=24300,
        target_1=24700,
        target_2=24900,
    )

    assert long_trade.side == PositionSide.LONG

    short_trade = bridge.process(
        symbol="NIFTY",
        signal="SELL",
        entry=24400,
        stop_loss=24600,
        target_1=24200,
        target_2=24000,
    )

    assert long_trade.exit_reason == "Signal Reversal"
    assert short_trade.side == PositionSide.SHORT

    assert len(engine.trades) == 2