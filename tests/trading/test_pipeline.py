"""
Tests for BATIP Trading Pipeline.
"""

from batip.trading.pipeline import (
    PipelineInput,
    TradingPipeline,
)


def strong_long() -> PipelineInput:
    return PipelineInput(
        symbol="RELIANCE",
        stock_score=10,
        technical_score=10,
        market_score=10,
        sector_score=10,
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
    )


def strong_short() -> PipelineInput:
    return PipelineInput(
        symbol="INFY",
        stock_score=-10,
        technical_score=-10,
        market_score=-10,
        sector_score=-10,
        entry=100.0,
        stop_loss=105.0,
        target_1=90.0,
        target_2=80.0,
    )


def watch_input() -> PipelineInput:
    return PipelineInput(
        symbol="TCS",
        stock_score=5,
        technical_score=1,
        market_score=0,
        sector_score=0,
    )


def test_pipeline_creation():
    pipeline = TradingPipeline()

    assert pipeline is not None
    assert pipeline.orchestrator is not None


def test_evaluate_long():
    pipeline = TradingPipeline()

    decision = pipeline.evaluate(
        strong_long()
    )

    assert decision.symbol == "RELIANCE"
    assert decision.trade_action == "TRADE"
    assert decision.direction == "Bullish"


def test_evaluate_short():
    pipeline = TradingPipeline()

    decision = pipeline.evaluate(
        strong_short()
    )

    assert decision.symbol == "INFY"
    assert decision.trade_action == "TRADE"
    assert decision.direction == "Bearish"


def test_watch_is_not_trade():
    pipeline = TradingPipeline()

    decision = pipeline.evaluate(
        watch_input()
    )

    assert decision.trade_action == "WATCH"


def test_evaluate_many():
    pipeline = TradingPipeline()

    decisions = pipeline.evaluate_many(
        [
            strong_long(),
            strong_short(),
            watch_input(),
        ]
    )

    assert len(decisions) == 3

    assert decisions[0].symbol == "RELIANCE"
    assert decisions[1].symbol == "INFY"
    assert decisions[2].symbol == "TCS"


def test_prepare_long_trade():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_long()
    )

    assert result.decision.trade_action == "TRADE"
    assert result.allocated is True
    assert result.order is not None
    assert result.order.side == "BUY"


def test_prepare_short_trade():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_short()
    )

    assert result.decision.trade_action == "TRADE"
    assert result.allocated is True
    assert result.order is not None
    assert result.order.side == "SELL"


def test_run_multiple_trades():
    pipeline = TradingPipeline(
        capital=100000,
        max_positions=2,
        max_portfolio_risk_percent=3.0,
    )

    result = pipeline.run(
        [
            strong_long(),
            strong_short(),
        ]
    )

    assert len(result.decisions) == 2
    assert len(result.run.allocation.positions) == 2
    assert len(result.orders) == 2
    assert result.run.allocation.valid is True


def test_run_excludes_watch():
    pipeline = TradingPipeline()

    result = pipeline.run(
        [
            strong_long(),
            watch_input(),
        ]
    )

    assert len(result.decisions) == 2
    assert len(result.run.allocation.positions) == 1
    assert len(result.orders) == 1


def test_fill_order():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_long()
    )

    assert result.order is not None

    order_id = result.order.order_id

    filled = pipeline.fill_order(
        order_id,
        101.0,
    )

    assert filled is not None
    assert filled.status == "FILLED"
    assert filled.fill_price == 101.0


def test_cancel_order():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_long()
    )

    assert result.order is not None

    cancelled = pipeline.cancel_order(
        result.order.order_id
    )

    assert cancelled is not None
    assert cancelled.status == "CANCELLED"


def test_summary():
    pipeline = TradingPipeline(
        max_positions=2,
    )

    result = pipeline.run(
        [
            strong_long(),
            strong_short(),
            watch_input(),
        ]
    )

    summary = pipeline.summary(result)

    assert summary["total_inputs"] == 3
    assert summary["trade_decisions"] == 2
    assert summary["watch_decisions"] == 1
    assert summary["avoid_decisions"] == 0
    assert summary["allocated_positions"] == 2
    assert summary["orders_created"] == 2
    assert summary["allocation_valid"] is True


def test_rejected_orders():
    pipeline = TradingPipeline()

    first = pipeline.prepare(
        strong_long()
    )

    assert first.order is not None

    second = pipeline.prepare(
        strong_long()
    )

    assert second.order is not None
    assert second.order.status == "REJECTED"

    rejected = pipeline.rejected_orders()

    assert len(rejected) == 1
    assert rejected[0].symbol == "RELIANCE"
    assert rejected[0].reason == (
        "Active order already exists for symbol"
    )


def test_get_order():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_long()
    )

    assert result.order is not None

    order = pipeline.get_order(
        result.order.order_id
    )

    assert order is not None
    assert order.order_id == result.order.order_id


def test_open_orders():
    pipeline = TradingPipeline()

    result = pipeline.prepare(
        strong_long()
    )

    assert result.order is not None

    open_orders = pipeline.open_orders()

    assert len(open_orders) == 1
    assert open_orders[0].order_id == (
        result.order.order_id
    )