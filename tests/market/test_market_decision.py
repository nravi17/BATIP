from batip.market.decision import (
    MarketDecisionEngine,
    MarketDecisionSnapshot,
)


def test_market_decision_engine_imports():
    engine = MarketDecisionEngine()

    assert engine is not None


def test_bullish_market_decision():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bullish",
        market_regime="Risk-On",
        breadth_score=2,
        sector_score=4,
        stock_score=8,
        confidence=90.0,
    )

    assert isinstance(result, MarketDecisionSnapshot)
    assert result.action == "BUY"
    assert result.direction == "Bullish"


def test_bearish_market_decision():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bearish",
        market_regime="Risk-Off",
        breadth_score=-2,
        sector_score=-4,
        stock_score=-8,
        confidence=90.0,
    )

    assert result.action == "SELL"
    assert result.direction == "Bearish"


def test_neutral_market_decision():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Neutral",
        market_regime="Neutral",
        breadth_score=0,
        sector_score=0,
        stock_score=0,
        confidence=50.0,
    )

    assert result.action == "WATCH"
    assert result.direction == "Neutral"


def test_low_confidence_bullish_market_is_watch():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bullish",
        market_regime="Risk-On",
        breadth_score=2,
        sector_score=4,
        stock_score=8,
        confidence=55.0,
    )

    assert result.action == "WATCH"


def test_high_confidence_bullish_market_is_buy():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bullish",
        market_regime="Risk-On",
        breadth_score=2,
        sector_score=4,
        stock_score=8,
        confidence=80.0,
    )

    assert result.action == "BUY"


def test_high_confidence_bearish_market_is_sell():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bearish",
        market_regime="Risk-Off",
        breadth_score=-2,
        sector_score=-4,
        stock_score=-8,
        confidence=80.0,
    )

    assert result.action == "SELL"


def test_decision_score_is_aggregated():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bullish",
        market_regime="Risk-On",
        breadth_score=2,
        sector_score=4,
        stock_score=8,
        confidence=90.0,
    )

    assert result.decision_score == 14


def test_decision_snapshot_contains_market_context():
    engine = MarketDecisionEngine()

    result = engine.analyze(
        market_bias="Bullish",
        market_regime="Risk-On",
        breadth_score=2,
        sector_score=4,
        stock_score=8,
        confidence=90.0,
    )

    assert result.market_bias == "Bullish"
    assert result.market_regime == "Risk-On"
    assert result.breadth_score == 2
    assert result.sector_score == 4
    assert result.stock_score == 8
    assert result.confidence == 90.0