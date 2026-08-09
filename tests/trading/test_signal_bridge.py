from batip.trading.signal_bridge import (
    SignalBridgeResult,
    StrategySignalBridge,
)
from batip.trading.strategy import TradingSignal


def test_generate_long_signal():
    signal = StrategySignalBridge.generate(
        symbol="RELIANCE",
        direction="Bullish",
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
        trend_score=90.0,
        momentum_score=85.0,
        volume_score=80.0,
    )

    assert signal is not None
    assert signal.symbol == "RELIANCE"
    assert signal.direction == "LONG"
    assert signal.signal == "TRADE"


def test_generate_short_signal_preserves_bearish_direction():
    signal = StrategySignalBridge.generate(
        symbol="INFY",
        direction="Bearish",
        entry=100.0,
        stop_loss=105.0,
        target_1=90.0,
        target_2=80.0,
        trend_score=90.0,
        momentum_score=85.0,
        volume_score=80.0,
    )

    assert signal is not None
    assert signal.symbol == "INFY"
    assert signal.direction == "SHORT"
    assert signal.signal == "TRADE"


def test_generate_watch_signal():
    signal = StrategySignalBridge.generate(
        symbol="TCS",
        direction="LONG",
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
        trend_score=70.0,
        momentum_score=55.0,
        volume_score=50.0,
    )

    assert signal is not None
    assert signal.signal == "WATCH"


def test_invalid_setup_returns_none():
    signal = StrategySignalBridge.generate(
        symbol="RELIANCE",
        direction="LONG",
        entry=100.0,
        stop_loss=105.0,
        target_1=110.0,
        target_2=120.0,
    )

    assert signal is None


def test_bridge_preserves_signal():
    signal = StrategySignalBridge.generate(
        symbol="RELIANCE",
        direction="LONG",
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
        trend_score=90.0,
        momentum_score=85.0,
        volume_score=80.0,
    )

    assert signal is not None

    result = StrategySignalBridge.from_signal(
        signal,
        stock_score=9,
        technical_score=8,
        market_score=3,
        sector_score=2,
    )

    assert isinstance(result, SignalBridgeResult)
    assert result.signal is signal
    assert result.stock_score == 9
    assert result.technical_score == 8
    assert result.market_score == 3
    assert result.sector_score == 2


def test_bridge_clamps_scores():
    signal = StrategySignalBridge.generate(
        symbol="RELIANCE",
        direction="LONG",
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
        trend_score=90.0,
        momentum_score=85.0,
        volume_score=80.0,
    )

    assert signal is not None

    result = StrategySignalBridge.from_signal(
        signal,
        stock_score=100,
        technical_score=-100,
        market_score=50,
        sector_score=-50,
    )

    assert result.stock_score == 10
    assert result.technical_score == -10
    assert result.market_score == 10
    assert result.sector_score == -10