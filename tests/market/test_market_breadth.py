from batip.market.market import (
    MarketBreadthEngine,
    MarketBreadthSnapshot,
)


def test_bullish_breadth():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=700,
        declines=200,
        unchanged=100,
    )

    assert isinstance(result, MarketBreadthSnapshot)
    assert result.total_stocks == 1000
    assert result.advance_percent == 70.0
    assert result.decline_percent == 20.0
    assert result.score == 2
    assert result.direction == "Bullish"
    assert result.breadth_status == "Strong Positive Breadth"


def test_positive_breadth():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=600,
        declines=300,
        unchanged=100,
    )

    assert result.score == 1
    assert result.direction == "Bullish"
    assert result.breadth_status == "Positive Breadth"


def test_neutral_breadth():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=400,
        declines=400,
        unchanged=200,
    )

    assert result.score == 0
    assert result.direction == "Neutral"
    assert result.breadth_status == "Neutral Breadth"


def test_negative_breadth():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=300,
        declines=600,
        unchanged=100,
    )

    assert result.score == -1
    assert result.direction == "Bearish"
    assert result.breadth_status == "Negative Breadth"


def test_strong_negative_breadth():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=200,
        declines=700,
        unchanged=100,
    )

    assert result.score == -2
    assert result.direction == "Bearish"
    assert result.breadth_status == "Strong Negative Breadth"


def test_ad_ratio():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=600,
        declines=300,
        unchanged=100,
    )

    assert result.ad_ratio == 2.0


def test_zero_declines():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=100,
        declines=0,
        unchanged=0,
    )

    assert result.ad_ratio == float("inf")


def test_empty_market():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=0,
        declines=0,
        unchanged=0,
    )

    assert result.total_stocks == 0
    assert result.advance_percent == 0.0
    assert result.decline_percent == 0.0
    assert result.ad_ratio == 0.0
    assert result.score == 0
    assert result.direction == "Neutral"


def test_negative_values_are_clamped():
    engine = MarketBreadthEngine()

    result = engine.analyze(
        advances=-10,
        declines=100,
        unchanged=20,
    )

    assert result.advances == 0
    assert result.declines == 100
    assert result.unchanged == 20
    assert result.total_stocks == 120


def test_percent_calculation():
    assert MarketBreadthEngine.calculate_percent(500, 1000) == 50.0
    assert MarketBreadthEngine.calculate_percent(0, 0) == 0.0


def test_score_boundaries():
    assert MarketBreadthEngine.breadth_score(70, 20) == 2
    assert MarketBreadthEngine.breadth_score(55, 30) == 1
    assert MarketBreadthEngine.breadth_score(50, 50) == 0
    assert MarketBreadthEngine.breadth_score(30, 55) == -1
    assert MarketBreadthEngine.breadth_score(20, 70) == -2