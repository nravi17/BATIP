from batip.market.stock import (
    StockMomentumEngine,
    StockMomentumSnapshot,
)


def make_momentum(
    symbol: str,
    momentum_percent: float,
    previous_momentum_percent: float = 0.0,
) -> StockMomentumSnapshot:
    return StockMomentumSnapshot(
        symbol=symbol,
        momentum_percent=momentum_percent,
        previous_momentum_percent=previous_momentum_percent,
    )


def test_strong_positive_momentum_score():
    engine = StockMomentumEngine()

    assert engine.score_momentum(2.0) == 2


def test_positive_momentum_score():
    engine = StockMomentumEngine()

    assert engine.score_momentum(0.50) == 1


def test_neutral_momentum_score():
    engine = StockMomentumEngine()

    assert engine.score_momentum(0.0) == 0


def test_negative_momentum_score():
    engine = StockMomentumEngine()

    assert engine.score_momentum(-0.50) == -1


def test_strong_negative_momentum_score():
    engine = StockMomentumEngine()

    assert engine.score_momentum(-2.0) == -2


def test_momentum_direction():
    engine = StockMomentumEngine()

    assert engine.direction_from_score(2) == "Bullish"
    assert engine.direction_from_score(1) == "Bullish"
    assert engine.direction_from_score(0) == "Neutral"
    assert engine.direction_from_score(-1) == "Bearish"
    assert engine.direction_from_score(-2) == "Bearish"


def test_momentum_acceleration():
    engine = StockMomentumEngine()

    result = engine.analyze(
        make_momentum(
            "TCS",
            momentum_percent=2.0,
            previous_momentum_percent=1.0,
        )
    )

    assert result.momentum_change == 1.0
    assert result.acceleration == "Accelerating"


def test_momentum_deceleration():
    engine = StockMomentumEngine()

    result = engine.analyze(
        make_momentum(
            "TCS",
            momentum_percent=0.50,
            previous_momentum_percent=1.50,
        )
    )

    assert result.momentum_change == -1.0
    assert result.acceleration == "Decelerating"


def test_momentum_stable():
    engine = StockMomentumEngine()

    result = engine.analyze(
        make_momentum(
            "TCS",
            momentum_percent=1.0,
            previous_momentum_percent=1.0,
        )
    )

    assert result.momentum_change == 0.0
    assert result.acceleration == "Stable"


def test_momentum_analysis():
    engine = StockMomentumEngine()

    result = engine.analyze(
        make_momentum(
            "TCS",
            momentum_percent=2.0,
            previous_momentum_percent=1.0,
        )
    )

    assert result.symbol == "TCS"
    assert result.score == 2
    assert result.direction == "Bullish"
    assert result.acceleration == "Accelerating"


def test_empty_symbol_is_supported():
    engine = StockMomentumEngine()

    result = engine.analyze(
        make_momentum(
            "",
            momentum_percent=0.0,
            previous_momentum_percent=0.0,
        )
    )

    assert result.symbol == ""
    assert result.score == 0
    assert result.direction == "Neutral"