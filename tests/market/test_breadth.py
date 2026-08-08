from batip.market.breadth import BreadthAnalyzer


def test_strong_bullish_breadth():
    result = BreadthAnalyzer.calculate(
        advances=700,
        declines=200,
        unchanged=100,
    )

    assert result.advances == 700
    assert result.declines == 200
    assert result.unchanged == 100
    assert result.advance_decline_ratio == 3.5
    assert result.score == 2
    assert result.signal == "Strong Bullish"


def test_bullish_breadth():
    result = BreadthAnalyzer.calculate(
        advances=600,
        declines=400,
    )

    assert result.score == 1
    assert result.signal == "Bullish"


def test_neutral_breadth():
    result = BreadthAnalyzer.calculate(
        advances=500,
        declines=500,
    )

    assert result.advance_decline_ratio == 1.0
    assert result.score == 0
    assert result.signal == "Neutral"


def test_bearish_breadth():
    result = BreadthAnalyzer.calculate(
        advances=400,
        declines=600,
    )

    assert result.score == -1
    assert result.signal == "Bearish"


def test_strong_bearish_breadth():
    result = BreadthAnalyzer.calculate(
        advances=200,
        declines=700,
        unchanged=100,
    )

    assert result.advance_decline_ratio == 0.29
    assert result.score == -2
    assert result.signal == "Strong Bearish"


def test_no_declines():
    result = BreadthAnalyzer.calculate(
        advances=100,
        declines=0,
    )

    assert result.advance_decline_ratio == 100.0
    assert result.score == 2
    assert result.signal == "Strong Bullish"


def test_empty_market():
    result = BreadthAnalyzer.calculate(
        advances=0,
        declines=0,
        unchanged=0,
    )

    assert result.advance_decline_ratio == 0.0
    assert result.score == 0
    assert result.signal == "Neutral"


def test_negative_values_are_sanitized():
    result = BreadthAnalyzer.calculate(
        advances=-100,
        declines=500,
        unchanged=-20,
    )

    assert result.advances == 0
    assert result.declines == 500
    assert result.unchanged == 0
    assert result.score == -2