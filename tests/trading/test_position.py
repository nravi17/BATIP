from batip.trading.position import (
    PaperPosition,
    PaperPositionEngine,
)


def test_open_long_position():
    engine = PaperPositionEngine()

    position = engine.open_position(
        symbol="RELIANCE",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    assert isinstance(position, PaperPosition)
    assert position.symbol == "RELIANCE"
    assert position.direction == "Bullish"
    assert position.quantity == 20
    assert position.status == "OPEN"
    assert position.capital_deployed == 2000
    assert position.maximum_loss == 100


def test_long_unrealized_profit():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    position = engine.update_price("TEST", 108)

    assert position.unrealized_pnl == 160
    assert position.status == "OPEN"


def test_long_target_one_hit():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    position = engine.update_price("TEST", 110)

    assert position.target_1_hit is True
    assert position.target_2_hit is False
    assert position.status == "OPEN"


def test_long_target_two_closes_position():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    position = engine.update_price("TEST", 120)

    assert position.status == "CLOSED"
    assert position.target_1_hit is True
    assert position.target_2_hit is True
    assert position.realized_pnl == 400
    assert position.unrealized_pnl == 0


def test_long_stop_loss_closes_position():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    position = engine.update_price("TEST", 94)

    assert position.status == "CLOSED"
    assert position.stop_loss_hit is True
    assert position.realized_pnl == -100


def test_open_short_position():
    engine = PaperPositionEngine()

    position = engine.open_position(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=20,
    )

    assert position.direction == "Bearish"
    assert position.maximum_loss == 100


def test_short_unrealized_profit():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=20,
    )

    position = engine.update_price("TEST", 92)

    assert position.unrealized_pnl == 160
    assert position.status == "OPEN"


def test_short_target_two_closes_position():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=20,
    )

    position = engine.update_price("TEST", 80)

    assert position.status == "CLOSED"
    assert position.target_2_hit is True
    assert position.realized_pnl == 400


def test_short_stop_loss_closes_position():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=20,
    )

    position = engine.update_price("TEST", 106)

    assert position.status == "CLOSED"
    assert position.stop_loss_hit is True
    assert position.realized_pnl == -100


def test_manual_close():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    pnl = engine.close_position(
        "TEST",
        105,
    )

    assert pnl == 100

    position = engine.get_position("TEST")

    assert position.status == "CLOSED"
    assert position.realized_pnl == 100
    assert position.unrealized_pnl == 0


def test_portfolio_pnl():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="A",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=10,
    )

    engine.open_position(
        symbol="B",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        quantity=10,
    )

    engine.update_price("A", 105)
    engine.update_price("B", 95)

    assert engine.total_unrealized_pnl() == 100
    assert engine.total_realized_pnl() == 0
    assert engine.total_pnl() == 100


def test_duplicate_open_position_is_rejected():
    engine = PaperPositionEngine()

    engine.open_position(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        quantity=20,
    )

    try:
        engine.open_position(
            symbol="TEST",
            direction="Bullish",
            entry=100,
            stop_loss=95,
            target_1=110,
            target_2=120,
            quantity=20,
        )
        assert False
    except ValueError as exc:
        assert "already exists" in str(exc)


def test_missing_position_is_rejected():
    engine = PaperPositionEngine()

    try:
        engine.get_position("UNKNOWN")
        assert False
    except KeyError as exc:
        assert "UNKNOWN" in str(exc)