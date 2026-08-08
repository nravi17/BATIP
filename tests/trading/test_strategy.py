from batip.trading.strategy import StrategyEngine, TradingSignal


def test_long_trade_signal_creation():
    signal = StrategyEngine.generate_signal(
        symbol="RELIANCE",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=120,
        target_2=140,
        trend_score=90,
        momentum_score=85,
        volume_score=80,
    )

    assert isinstance(signal, TradingSignal)
    assert signal.symbol == "RELIANCE"
    assert signal.direction == "LONG"
    assert signal.entry == 100
    assert signal.stop_loss == 90
    assert signal.target_1 == 120
    assert signal.target_2 == 140


def test_short_trade_signal_creation():
    signal = StrategyEngine.generate_signal(
        symbol="INFY",
        direction="SELL",
        entry=100,
        stop_loss=110,
        target_1=80,
        target_2=60,
        trend_score=90,
        momentum_score=85,
        volume_score=80,
    )

    assert signal.direction == "SHORT"
    assert signal.symbol == "INFY"


def test_risk_reward_calculation():
    ratio = StrategyEngine.calculate_risk_reward(
        entry=100,
        stop_loss=90,
        target=120,
    )

    assert ratio == 2.0


def test_short_risk_reward_calculation():
    ratio = StrategyEngine.calculate_risk_reward(
        entry=100,
        stop_loss=110,
        target=80,
    )

    assert ratio == 2.0


def test_zero_risk_returns_zero():
    ratio = StrategyEngine.calculate_risk_reward(
        entry=100,
        stop_loss=100,
        target=120,
    )

    assert ratio == 0.0


def test_high_score_is_trade():
    score = StrategyEngine.calculate_score(
        trend_score=100,
        momentum_score=100,
        volume_score=100,
        risk_reward=3,
    )

    assert score == 100.0
    assert StrategyEngine.classify_signal(score) == "TRADE"


def test_medium_score_is_watch():
    score = StrategyEngine.calculate_score(
        trend_score=60,
        momentum_score=60,
        volume_score=60,
        risk_reward=1.5,
    )

    assert StrategyEngine.classify_signal(score) == "WATCH"


def test_low_score_is_avoid():
    score = StrategyEngine.calculate_score(
        trend_score=20,
        momentum_score=20,
        volume_score=20,
        risk_reward=0.5,
    )

    assert StrategyEngine.classify_signal(score) == "AVOID"


def test_invalid_long_setup():
    valid, reason = StrategyEngine.validate_setup(
        direction="LONG",
        entry=100,
        stop_loss=105,
        target_1=120,
        target_2=140,
    )

    assert valid is False
    assert "stop loss" in reason.lower()


def test_invalid_short_setup():
    valid, reason = StrategyEngine.validate_setup(
        direction="SHORT",
        entry=100,
        stop_loss=95,
        target_1=80,
        target_2=60,
    )

    assert valid is False
    assert "stop loss" in reason.lower()


def test_invalid_long_target():
    valid, reason = StrategyEngine.validate_setup(
        direction="LONG",
        entry=100,
        stop_loss=90,
        target_1=95,
        target_2=120,
    )

    assert valid is False
    assert "target 1" in reason.lower()


def test_invalid_short_target():
    valid, reason = StrategyEngine.validate_setup(
        direction="SHORT",
        entry=100,
        stop_loss=110,
        target_1=105,
        target_2=80,
    )

    assert valid is False
    assert "target 1" in reason.lower()


def test_unknown_direction():
    valid, reason = StrategyEngine.validate_setup(
        direction="UNKNOWN",
        entry=100,
        stop_loss=90,
        target_1=120,
        target_2=140,
    )

    assert valid is False
    assert "unknown" in reason.lower()


def test_bad_risk_reward_forces_avoid():
    signal = StrategyEngine.generate_signal(
        symbol="TCS",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=105,
        target_2=110,
        trend_score=100,
        momentum_score=100,
        volume_score=100,
        minimum_risk_reward=1.5,
    )

    assert signal.risk_reward == 0.5
    assert signal.signal == "AVOID"
    assert "risk/reward" in signal.reason.lower()


def test_trade_signal_for_strong_setup():
    signal = StrategyEngine.generate_signal(
        symbol="RELIANCE",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=120,
        target_2=140,
        trend_score=90,
        momentum_score=85,
        volume_score=80,
    )

    assert signal.signal == "TRADE"
    assert signal.score >= 70
    assert signal.risk_reward >= 1.5


def test_watch_signal_for_medium_setup():
    signal = StrategyEngine.generate_signal(
        symbol="HDFCBANK",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=115,
        target_2=125,
        trend_score=60,
        momentum_score=60,
        volume_score=60,
    )

    assert signal.signal == "WATCH"


def test_symbol_is_normalized():
    signal = StrategyEngine.generate_signal(
        symbol=" reliance ",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=120,
        target_2=140,
        trend_score=90,
        momentum_score=90,
        volume_score=90,
    )

    assert signal.symbol == "RELIANCE"


def test_empty_symbol_is_rejected():
    try:
        StrategyEngine.generate_signal(
            symbol="",
            direction="BUY",
            entry=100,
            stop_loss=90,
            target_1=120,
            target_2=140,
            trend_score=90,
            momentum_score=90,
            volume_score=90,
        )
        assert False
    except ValueError as exc:
        assert "symbol" in str(exc).lower()


def test_evaluate_returns_none_for_invalid_setup():
    result = StrategyEngine.evaluate(
        symbol="RELIANCE",
        direction="BUY",
        entry=100,
        stop_loss=105,
        target_1=120,
        target_2=140,
        trend_score=90,
        momentum_score=90,
        volume_score=90,
    )

    assert result is None


def test_evaluate_returns_signal_for_valid_setup():
    result = StrategyEngine.evaluate(
        symbol="RELIANCE",
        direction="BUY",
        entry=100,
        stop_loss=90,
        target_1=120,
        target_2=140,
        trend_score=90,
        momentum_score=90,
        volume_score=90,
    )

    assert isinstance(result, TradingSignal)