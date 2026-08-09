from batip.paper.engine import PaperTradingEngine
from batip.paper.models import PositionSide, TradeStatus


def test_open_long_trade():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    assert trade.symbol == "RELIANCE"
    assert trade.side == PositionSide.LONG
    assert trade.entry == 100
    assert trade.quantity == 10
    assert trade.status == TradeStatus.OPEN


def test_open_short_trade():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.SHORT,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    assert trade.symbol == "INFY"
    assert trade.side == PositionSide.SHORT
    assert trade.status == TradeStatus.OPEN


def test_long_target_one():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.update_trade(trade, 110)

    assert trade.status == TradeStatus.TARGET_1
    assert trade.exit_price is None


def test_long_target_two_closes_trade():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.update_trade(trade, 120)

    assert trade.status == TradeStatus.TARGET_2
    assert trade.exit_price == 120
    assert trade.exit_reason == "Target 2"


def test_long_stop_loss():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.update_trade(trade, 95)

    assert trade.status == TradeStatus.STOPPED
    assert trade.exit_price == 95
    assert trade.exit_reason == "Stop Loss"


def test_short_target_one():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.SHORT,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    engine.update_trade(trade, 90)

    assert trade.status == TradeStatus.TARGET_1
    assert trade.exit_price is None


def test_short_target_two_closes_trade():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.SHORT,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    engine.update_trade(trade, 80)

    assert trade.status == TradeStatus.TARGET_2
    assert trade.exit_price == 80
    assert trade.exit_reason == "Target 2"


def test_short_stop_loss():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.SHORT,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    engine.update_trade(trade, 105)

    assert trade.status == TradeStatus.STOPPED
    assert trade.exit_price == 105
    assert trade.exit_reason == "Stop Loss"


def test_manual_close():
    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="TCS",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.close_trade(
        trade,
        price=107,
        reason="Manual Exit",
    )

    assert trade.status == TradeStatus.CLOSED
    assert trade.exit_price == 107
    assert trade.exit_reason == "Manual Exit"


def test_open_and_closed_trades():
    engine = PaperTradingEngine()

    open_trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    closed_trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.SHORT,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    engine.close_trade(
        closed_trade,
        price=95,
        reason="Manual Exit",
    )

    assert open_trade in engine.open_trades()
    assert closed_trade not in engine.open_trades()

    assert closed_trade in engine.closed_trades()
    assert open_trade not in engine.closed_trades()


def test_total_pnl():
    engine = PaperTradingEngine()

    winning_trade = engine.open_trade(
        symbol="RELIANCE",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    losing_trade = engine.open_trade(
        symbol="INFY",
        side=PositionSide.LONG,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.close_trade(
        winning_trade,
        price=110,
        reason="Target 1",
    )

    engine.close_trade(
        losing_trade,
        price=95,
        reason="Stop Loss",
    )

    assert winning_trade.pnl == 100
    assert losing_trade.pnl == -50
    assert engine.total_pnl() == 50