from batip.trading.setup import TradeSetupEngine


def test_valid_long_setup():
    engine = TradeSetupEngine(
        capital=100000,
        risk_percent=1,
        minimum_risk_reward=1.5,
    )

    result = engine.build(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        intraday="FAVORABLE",
        overnight="FAVORABLE",
        confidence=90,
    )

    assert result.valid is True
    assert result.position_size == 20
    assert result.risk_per_share == 5
    assert result.risk_reward_1 == 2
    assert result.risk_reward_2 == 4
    assert result.maximum_loss == 100
    assert result.invalidation == "Below 95"
    assert result.confidence == 90


def test_valid_short_setup():
    engine = TradeSetupEngine(
        capital=100000,
        risk_percent=1,
        minimum_risk_reward=1.5,
    )

    result = engine.build(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=105,
        target_1=90,
        target_2=80,
        intraday="FAVORABLE",
        overnight="FAVORABLE",
        confidence=85,
    )

    assert result.valid is True
    assert result.position_size == 20
    assert result.risk_per_share == 5
    assert result.risk_reward_1 == 2
    assert result.risk_reward_2 == 4
    assert result.maximum_loss == 100
    assert result.invalidation == "Above 105"


def test_invalid_long_setup():
    engine = TradeSetupEngine()

    result = engine.build(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=105,
        target_1=110,
        target_2=120,
    )

    assert result.valid is False
    assert result.position_size == 20
    assert "stop loss" in result.reason.lower()


def test_invalid_short_setup():
    engine = TradeSetupEngine()

    result = engine.build(
        symbol="TEST",
        direction="Bearish",
        entry=100,
        stop_loss=95,
        target_1=90,
        target_2=80,
    )

    assert result.valid is False
    assert result.position_size == 20
    assert "stop loss" in result.reason.lower()


def test_bad_risk_reward_setup():
    engine = TradeSetupEngine(
        minimum_risk_reward=1.5,
    )

    result = engine.build(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=90,
        target_1=105,
        target_2=110,
    )

    assert result.valid is False
    assert result.risk_reward_1 == 0.5
    assert "risk/reward" in result.reason.lower()


def test_confidence_is_clamped():
    engine = TradeSetupEngine()

    high = engine.build(
        symbol="HIGH",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        confidence=150,
    )

    low = engine.build(
        symbol="LOW",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        confidence=-20,
    )

    assert high.confidence == 100
    assert low.confidence == 0


def test_trading_context_is_preserved():
    engine = TradeSetupEngine()

    result = engine.build(
        symbol="TEST",
        direction="Bullish",
        entry=100,
        stop_loss=95,
        target_1=110,
        target_2=120,
        intraday="FAVORABLE",
        overnight="WATCH",
        confidence=88,
    )

    assert result.intraday == "FAVORABLE"
    assert result.overnight == "WATCH"
    assert result.confidence == 88