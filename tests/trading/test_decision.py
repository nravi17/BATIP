from batip.trading.decision import TradeDecisionEngine


def test_strong_bullish_trade_decision():
    engine = TradeDecisionEngine()

    result = engine.evaluate(
        symbol="TEST",
        stock_score=10,
        technical_score=10,
        market_score=2,
        sector_score=2,
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
    )

    assert result.symbol == "TEST"
    assert result.opportunity_score == 14
    assert result.recommendation == "STRONG BUY"
    assert result.direction == "Bullish"
    assert result.confidence == 95
    assert result.intraday == "FAVORABLE"
    assert result.overnight == "FAVORABLE"
    assert result.trade_action == "TRADE"

    assert result.setup is not None
    assert result.setup.valid is True
    assert result.setup.position_size == 20
    assert result.setup.risk_per_share == 5
    assert result.setup.maximum_loss == 100


def test_bearish_trade_decision():
    engine = TradeDecisionEngine()

    result = engine.evaluate(
        symbol="TEST",
        stock_score=-10,
        technical_score=-10,
        market_score=-2,
        sector_score=-2,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
    )

    assert result.opportunity_score == -6
    assert result.recommendation == "SELL"
    assert result.direction == "Bearish"
    assert result.confidence == 79
    assert result.trade_action == "WATCH"

    assert result.setup is not None
    assert result.setup.valid is True
    assert result.setup.position_size == 20


def test_trade_requires_price_levels():
    engine = TradeDecisionEngine()

    result = engine.evaluate(
        symbol="TEST",
        stock_score=10,
        technical_score=10,
        market_score=2,
        sector_score=2,
    )

    assert result.recommendation == "STRONG BUY"
    assert result.trade_action == "WATCH"
    assert result.setup is None

    assert any(
        "trade levels" in reason.lower()
        for reason in result.reasons
    )


def test_invalid_trade_setup_becomes_avoid():
    engine = TradeDecisionEngine()

    result = engine.evaluate(
        symbol="TEST",
        stock_score=10,
        technical_score=10,
        market_score=2,
        sector_score=2,
        entry=100,
        stop_loss=105,
        target_1=110,
        target_2=120,
    )

    assert result.setup is not None
    assert result.setup.valid is False
    assert result.trade_action == "AVOID"

    assert any(
        "stop loss" in reason.lower()
        for reason in result.reasons
    )


def test_watch_opportunity_remains_watch():
    engine = TradeDecisionEngine()

    result = engine.evaluate(
        symbol="TEST",
        stock_score=1,
        technical_score=0,
        market_score=0,
        sector_score=0,
    )

    assert result.recommendation == "WATCH"
    assert result.trade_action == "WATCH"
    assert result.setup is None


def test_bearish_setup_with_valid_levels():
    engine = TradeDecisionEngine(
        capital=100000,
        risk_percent=1,
        minimum_risk_reward=1.5,
    )

    result = engine.evaluate(
        symbol="TEST",
        stock_score=-10,
        technical_score=-10,
        market_score=-2,
        sector_score=-2,
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
    )

    assert result.trade_action == "WATCH"
    assert result.setup is not None
    assert result.setup.valid is True
    assert result.setup.risk_per_share == 5
    assert result.setup.risk_reward_1 == 2
    assert result.setup.risk_reward_2 == 4