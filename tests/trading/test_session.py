"""
Tests for BATIP Trading Session Manager.
"""

from batip.trading.orchestrator import TradingOrchestrator
from batip.trading.session import TradingSessionManager


def _strong_long(manager: TradingSessionManager):
    return manager.orchestrator.evaluate(
        symbol="RELIANCE",
        stock_score=10,
        technical_score=10,
        market_score=5,
        sector_score=5,
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
    )


def _strong_short(manager: TradingSessionManager):
    return manager.orchestrator.evaluate(
        symbol="INFY",
        stock_score=-10,
        technical_score=-10,
        market_score=-5,
        sector_score=-5,
        entry=100.0,
        stop_loss=105.0,
        target_1=90.0,
        target_2=80.0,
    )


def test_session_manager_creation():
    manager = TradingSessionManager()

    assert manager.session is None
    assert isinstance(
        manager.orchestrator,
        TradingOrchestrator,
    )


def test_start_session():
    manager = TradingSessionManager()

    session = manager.start("session-001")

    assert session.session_id == "session-001"
    assert session.status == "ACTIVE"
    assert session.started_at is not None


def test_cannot_start_duplicate_active_session():
    manager = TradingSessionManager()

    manager.start("session-001")

    try:
        manager.start("session-002")
        assert False
    except RuntimeError:
        assert True


def test_close_session():
    manager = TradingSessionManager()

    manager.start("session-001")
    session = manager.close()

    assert session.status == "CLOSED"
    assert session.closed_at is not None


def test_operations_require_active_session():
    manager = TradingSessionManager()

    try:
        manager.open_orders()
        assert False
    except RuntimeError:
        assert True


def test_prepare_long_trade():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None
    assert result.order.symbol == "RELIANCE"
    assert result.order.side == "BUY"
    assert result.order.status == "PENDING"

    assert len(manager.session.orders) == 1


def test_prepare_short_trade():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_short(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None
    assert result.order.symbol == "INFY"
    assert result.order.side == "SELL"
    assert result.order.status == "PENDING"


def test_fill_order_creates_paper_trade():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    order = manager.fill_order(
        result.order.order_id,
        101.0,
    )

    assert order is not None
    assert order.status == "FILLED"
    assert order.fill_price == 101.0

    trades = manager.open_trades()

    assert len(trades) == 1
    assert trades[0].symbol == "RELIANCE"
    assert trades[0].entry == 101.0


def test_cancel_order():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    order = manager.cancel_order(
        result.order.order_id
    )

    assert order is not None
    assert order.status == "CANCELLED"


def test_rejected_order_is_recorded():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    first = manager.prepare_trade(decision)

    assert first.order is not None

    second = manager.prepare_trade(decision)

    assert second.order is not None
    assert second.order.status == "REJECTED"

    rejected = manager.rejected_orders()

    assert len(rejected) == 1
    assert rejected[0].status == "REJECTED"


def test_update_trade_to_target_one():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    manager.fill_order(
        result.order.order_id,
        100.0,
    )

    trade = manager.open_trades()[0]

    updated = manager.update_trade(
        trade,
        110.0,
    )

    assert updated.status.name == "TARGET_1"


def test_update_trade_to_target_two():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    manager.fill_order(
        result.order.order_id,
        100.0,
    )

    trade = manager.open_trades()[0]

    updated = manager.update_trade(
        trade,
        120.0,
    )

    assert updated.status.name == "TARGET_2"


def test_manual_close_trade():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    manager.fill_order(
        result.order.order_id,
        100.0,
    )

    trade = manager.open_trades()[0]

    closed = manager.close_trade(
        trade,
        115.0,
    )

    assert closed.status.name == "CLOSED"

    assert len(manager.open_trades()) == 0
    assert len(manager.closed_trades()) == 1


def test_session_summary():
    manager = TradingSessionManager()
    manager.start("session-001")

    decision = _strong_long(manager)

    result = manager.prepare_trade(decision)

    assert result.order is not None

    summary = manager.summary()

    assert summary.session_id == "session-001"
    assert summary.status == "ACTIVE"
    assert summary.total_orders == 1
    assert summary.pending_orders == 1
    assert summary.filled_orders == 0


def test_closed_session_summary():
    manager = TradingSessionManager()
    manager.start("session-001")

    manager.close()

    summary = manager.summary()

    assert summary.status == "CLOSED"
    assert summary.closed_at is not None


def test_summary_before_session():
    manager = TradingSessionManager()

    summary = manager.summary()

    assert summary.status == "NOT_STARTED"
    assert summary.total_orders == 0
    assert summary.total_pnl == 0.0


def test_run_multiple_decisions():
    manager = TradingSessionManager(
        max_positions=2,
    )

    manager.start("session-001")

    long_decision = _strong_long(manager)
    short_decision = _strong_short(manager)

    result = manager.run(
        [
            long_decision,
            short_decision,
        ]
    )

    assert result.allocation.valid is True
    assert len(result.allocation.positions) == 2
    assert len(result.orders) == 2

    summary = manager.summary()

    assert summary.total_orders == 2
    assert summary.pending_orders == 2