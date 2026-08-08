from batip.trading.trade_manager import TradeManager


def test_trade_manager_creation():
    manager = TradeManager()

    assert manager is not None
    assert manager.trade_count() == 0


def test_calculate_position_size():
    manager = TradeManager()

    quantity = manager.calculate_position_size(
        capital=100000,
        risk_percent=1,
        entry=1520,
        stop_loss=1500,
    )

    assert quantity == 50


def test_prepare_long_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1500,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is not None
    assert trade.symbol == "RELIANCE"
    assert trade.side == "BUY"
    assert trade.quantity == 50
    assert trade.entry_price == 1520
    assert trade.stop_loss == 1500
    assert trade.target_1 == 1550
    assert trade.target_2 == 1580
    assert trade.risk_amount == 1000
    assert trade.risk_reward == 1.5
    assert trade.status == "PREPARED"


def test_prepare_short_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="INFY",
        direction="Bearish",
        entry=1520,
        stop_loss=1540,
        target_1=1490,
        target_2=1460,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is not None
    assert trade.symbol == "INFY"
    assert trade.side == "SELL"
    assert trade.quantity == 50
    assert trade.risk_amount == 1000
    assert trade.risk_reward == 1.5


def test_symbol_is_normalized():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol=" reliance ",
        direction="Bullish",
        entry=1520,
        stop_loss=1500,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is not None
    assert trade.symbol == "RELIANCE"


def test_invalid_setup_returns_none():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1530,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is None
    assert manager.trade_count() == 0


def test_zero_risk_produces_no_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1520,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is None


def test_get_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1500,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    result = manager.get_trade("RELIANCE")

    assert result is trade


def test_get_missing_trade():
    manager = TradeManager()

    assert manager.get_trade("RELIANCE") is None


def test_cancel_prepared_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1500,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is not None

    result = manager.cancel_trade("RELIANCE")

    assert result is True
    assert trade.status == "CANCELLED"


def test_cancel_missing_trade():
    manager = TradeManager()

    assert manager.cancel_trade("RELIANCE") is False


def test_cancel_already_cancelled_trade():
    manager = TradeManager()

    trade = manager.prepare_trade(
        symbol="RELIANCE",
        direction="Bullish",
        entry=1520,
        stop_loss=1500,
        target_1=1550,
        target_2=1580,
        score=90,
        capital=100000,
        risk_percent=1,
    )

    assert trade is not None

    assert manager.cancel_trade("RELIANCE") is True
    assert manager.cancel_trade("RELIANCE") is False