from batip.market.market import (
    MarketRegimeEngine,
    MarketRegimeSnapshot,
)


def test_strong_bullish_regime():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=10,
        bullish_sectors=8,
        bearish_sectors=2,
        top_stock_score=8,
    )

    assert isinstance(result, MarketRegimeSnapshot)
    assert result.regime == "BULLISH"
    assert result.risk_state == "RISK_ON"


def test_bullish_regime():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=4,
        bullish_sectors=6,
        bearish_sectors=4,
        top_stock_score=5,
    )

    assert result.regime == "BULLISH"
    assert result.risk_state == "RISK_ON"


def test_neutral_regime():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=0,
        bullish_sectors=5,
        bearish_sectors=5,
        top_stock_score=0,
    )

    assert result.regime == "NEUTRAL"
    assert result.risk_state == "RISK_OFF"


def test_bearish_regime():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=-4,
        bullish_sectors=4,
        bearish_sectors=6,
        top_stock_score=-5,
    )

    assert result.regime == "BEARISH"
    assert result.risk_state == "RISK_OFF"


def test_strong_bearish_regime():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=-10,
        bullish_sectors=2,
        bearish_sectors=8,
        top_stock_score=-8,
    )

    assert result.regime == "BEARISH"
    assert result.risk_state == "RISK_OFF"


def test_sector_breadth_is_bullish():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=3,
        bullish_sectors=7,
        bearish_sectors=3,
        top_stock_score=2,
    )

    assert result.breadth == "POSITIVE"


def test_sector_breadth_is_bearish():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=-3,
        bullish_sectors=3,
        bearish_sectors=7,
        top_stock_score=-2,
    )

    assert result.breadth == "NEGATIVE"


def test_sector_breadth_is_neutral():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=0,
        bullish_sectors=5,
        bearish_sectors=5,
        top_stock_score=0,
    )

    assert result.breadth == "NEUTRAL"


def test_regime_confidence_is_high_for_strong_alignment():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=10,
        bullish_sectors=9,
        bearish_sectors=1,
        top_stock_score=10,
    )

    assert result.confidence >= 80


def test_regime_confidence_is_lower_for_mixed_signals():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=0,
        bullish_sectors=5,
        bearish_sectors=5,
        top_stock_score=0,
    )

    assert result.confidence < 80


def test_empty_market_defaults_to_neutral():
    engine = MarketRegimeEngine()

    result = engine.analyze(
        market_score=0,
        bullish_sectors=0,
        bearish_sectors=0,
        top_stock_score=0,
    )

    assert result.regime == "NEUTRAL"
    assert result.risk_state == "RISK_OFF"
    assert result.breadth == "NEUTRAL"