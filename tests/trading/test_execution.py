from batip.trading.execution import ExecutionEngine


def test_create_buy_order():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    assert order.symbol == "RELIANCE"
    assert order.side == "BUY"
    assert order.quantity == 20
    assert order.entry == 100
    assert order.stop_loss == 95
    assert order.target_1 == 110
    assert order.target_2 == 120
    assert order.status == "PENDING"


def test_create_sell_order():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="HDFCBANK",
        side="SELL",
        quantity=20,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
    )

    assert order.symbol == "HDFCBANK"
    assert order.side == "SELL"
    assert order.status == "PENDING"


def test_fill_order():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    filled = engine.fill_order(
        order.order_id,
        fill_price=101,
    )

    assert filled.status == "FILLED"
    assert filled.fill_price == 101


def test_cancel_pending_order():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    cancelled = engine.cancel_order(order.order_id)

    assert cancelled.status == "CANCELLED"


def test_filled_order_cannot_be_cancelled():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    engine.fill_order(order.order_id, fill_price=100)

    result = engine.cancel_order(order.order_id)

    assert result.status == "FILLED"


def test_duplicate_order_is_rejected():
    engine = ExecutionEngine()

    engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    duplicate = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    assert duplicate.status == "REJECTED"


def test_invalid_quantity_is_rejected():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=0,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    assert order.status == "REJECTED"


def test_invalid_buy_levels_are_rejected():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="RELIANCE",
        side="BUY",
        quantity=20,
        entry=100,
        stop_loss=105,
        target_1=110,
        target_2=120,
    )

    assert order.status == "REJECTED"


def test_invalid_sell_levels_are_rejected():
    engine = ExecutionEngine()

    order = engine.create_order(
        symbol="HDFCBANK",
        side="SELL",
        quantity=20,
        entry=100,
        stop_loss=95,
        target_1=90,
        target_2=80,
    )

    assert order.status == "REJECTED"