from batip.trading.orchestrator import TradingOrchestrator


def _strong_long(orchestrator: TradingOrchestrator):
    return orchestrator.evaluate(
        symbol="RELIANCE",
        stock_score=95,
        technical_score=95,
        market_score=90,
        sector_score=90,
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
    )


def _strong_short(orchestrator: TradingOrchestrator):
    return orchestrator.evaluate(
        symbol="INFY",
        stock_score=95,
        technical_score=95,
        market_score=90,
        sector_score=90,
        entry=100.0,
        stop_loss=105.0,
        target_1=90.0,
        target_2=80.0,
    )


def test_orchestrator_creation():
    orchestrator = TradingOrchestrator()

    assert orchestrator.capital == 100000.0
    assert orchestrator.risk_percent == 1.0
    assert orchestrator.open_orders() == []


def test_evaluate_strong_long():
    orchestrator = TradingOrchestrator()

    decision = _strong_long(orchestrator)

    assert decision.symbol == "RELIANCE"
    assert decision.trade_action == "TRADE"
    assert decision.setup is not None
    assert decision.setup.valid is True


def test_evaluate_strong_short():
    orchestrator = TradingOrchestrator()

    decision = _strong_short(orchestrator)

    assert decision.symbol == "INFY"
    assert decision.trade_action == "TRADE"
    assert decision.setup is not None
    assert decision.setup.valid is True


def test_build_trade_candidate():
    orchestrator = TradingOrchestrator()

    decision = _strong_long(orchestrator)
    candidate = orchestrator.build_candidate(decision)

    assert candidate is not None
    assert candidate["symbol"] == "RELIANCE"
    assert candidate["action"] == "TRADE"
    assert candidate["position_size"] > 0
    assert candidate["maximum_loss"] > 0


def test_watch_decision_is_not_candidate():
    orchestrator = TradingOrchestrator()

    decision = orchestrator.evaluate(
        symbol="RELIANCE",
        stock_score=70,
        technical_score=70,
        market_score=70,
        sector_score=70,
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
    )

    assert decision.trade_action == "WATCH"
    assert orchestrator.build_candidate(decision) is None


def test_missing_levels_do_not_create_trade():
    orchestrator = TradingOrchestrator()

    decision = orchestrator.evaluate(
        symbol="RELIANCE",
        stock_score=95,
        technical_score=95,
        market_score=90,
        sector_score=90,
    )

    assert decision.trade_action == "WATCH"
    assert decision.setup is None

    result = orchestrator.prepare_trade(decision)

    assert result.order is None
    assert result.allocated is False


def test_prepare_long_trade():
    orchestrator = TradingOrchestrator()

    decision = _strong_long(orchestrator)
    result = orchestrator.prepare_trade(decision)

    assert result.allocated is True
    assert result.order is not None
    assert result.order.status == "PENDING"
    assert result.order.symbol == "RELIANCE"
    assert result.order.side == "BUY"
    assert result.order.quantity > 0


def test_prepare_short_trade():
    orchestrator = TradingOrchestrator()

    decision = _strong_short(orchestrator)
    result = orchestrator.prepare_trade(decision)

    assert result.allocated is True
    assert result.order is not None
    assert result.order.status == "PENDING"
    assert result.order.symbol == "INFY"
    assert result.order.side == "SELL"


def test_fill_order():
    orchestrator = TradingOrchestrator()

    decision = _strong_long(orchestrator)
    result = orchestrator.prepare_trade(decision)

    assert result.order is not None

    filled = orchestrator.fill_order(
        result.order.order_id,
        100.0,
    )

    assert filled is not None
    assert filled.status == "FILLED"
    assert filled.fill_price == 100.0


def test_cancel_order():
    orchestrator = TradingOrchestrator()

    decision = _strong_long(orchestrator)
    result = orchestrator.prepare_trade(decision)

    assert result.order is not None

    cancelled = orchestrator.cancel_order(
        result.order.order_id,
    )

    assert cancelled is not None
    assert cancelled.status == "CANCELLED"


def test_duplicate_symbol_is_rejected():
    orchestrator = TradingOrchestrator()

    first = orchestrator.prepare_trade(
        _strong_long(orchestrator)
    )

    assert first.order is not None
    assert first.order.status == "PENDING"

    second = orchestrator.prepare_trade(
        _strong_long(orchestrator)
    )

    assert second.order is not None
    assert second.order.status == "REJECTED"
    assert "already exists" in second.order.reason.lower()


def test_run_allocates_and_prepares():
    orchestrator = TradingOrchestrator(
        capital=100000,
        max_positions=2,
        max_portfolio_risk_percent=3.0,
    )

    long_decision = _strong_long(orchestrator)
    short_decision = _strong_short(orchestrator)

    result = orchestrator.run(
        [
            long_decision,
            short_decision,
        ]
    )

    assert result.allocation.valid is True
    assert len(result.allocation.positions) == 2
    assert len(result.orders) == 2

    assert all(
        order.status == "PENDING"
        for order in result.orders
    )


def test_run_respects_max_positions():
    orchestrator = TradingOrchestrator(
        capital=100000,
        max_positions=1,
        max_portfolio_risk_percent=3.0,
    )

    decisions = [
        _strong_long(orchestrator),
        _strong_short(orchestrator),
    ]

    result = orchestrator.run(decisions)

    assert len(result.allocation.positions) == 1
    assert len(result.orders) == 1


def test_get_order():
    orchestrator = TradingOrchestrator()

    result = orchestrator.prepare_trade(
        _strong_long(orchestrator)
    )

    assert result.order is not None

    order = orchestrator.get_order(
        result.order.order_id,
    )

    assert order is result.order


def test_rejected_orders():
    orchestrator = TradingOrchestrator()

    first = orchestrator.prepare_trade(
        _strong_long(orchestrator)
    )

    assert first.order is not None

    second = orchestrator.prepare_trade(
        _strong_long(orchestrator)
    )

    assert second.order is not None
    assert second.order.status == "REJECTED"

    rejected = orchestrator.rejected_orders()

    assert len(rejected) == 1
    assert rejected[0] is second.order