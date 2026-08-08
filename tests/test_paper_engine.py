from batip.paper.engine import PaperTradingEngine
from batip.paper.models import (
    PositionSide,
    TradeStatus,
)


def test_long_target_2():

    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="BANKNIFTY",
        side=PositionSide.LONG,
        entry=57700,
        stop_loss=57500,
        target_1=58000,
        target_2=58500,
    )

    engine.update_trade(
        trade,
        58500,
    )

    assert trade.status == TradeStatus.TARGET_2
    assert trade.exit_price == 58500
    assert trade.pnl == 800


def test_long_stop_loss():

    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="BANKNIFTY",
        side=PositionSide.LONG,
        entry=57700,
        stop_loss=57500,
        target_1=58000,
        target_2=58500,
    )

    engine.update_trade(
        trade,
        57500,
    )

    assert trade.status == TradeStatus.STOPPED
    assert trade.exit_price == 57500
    assert trade.pnl == -200


def test_short_target_2():

    engine = PaperTradingEngine()

    trade = engine.open_trade(
        symbol="BANKNIFTY",
        side=PositionSide.SHORT,
        entry=57700,
        stop_loss=58000,
        target_1=57000,
        target_2=56700,
    )

    engine.update_trade(
        trade,
        56700,
    )

    assert trade.status == TradeStatus.TARGET_2
    assert trade.exit_price == 56700
    assert trade.pnl == 1000