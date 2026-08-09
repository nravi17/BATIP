from batip.market.portfolio import (
    PortfolioScoringEngine,
    PortfolioScoreSnapshot,
)


def make_holding(
    symbol: str,
    strength_score: int,
    momentum_score: int,
    volume_score: int,
    signal_score: int,
    confidence: float,
):
    return {
        "symbol": symbol,
        "strength_score": strength_score,
        "momentum_score": momentum_score,
        "volume_score": volume_score,
        "signal_score": signal_score,
        "confidence": confidence,
    }


def test_portfolio_scoring_imports():
    engine = PortfolioScoringEngine()

    assert engine is not None


def test_strong_holding_score():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "TCS",
            strength_score=2,
            momentum_score=2,
            volume_score=2,
            signal_score=2,
            confidence=95.0,
        )
    )

    assert isinstance(result, PortfolioScoreSnapshot)
    assert result.symbol == "TCS"
    assert result.score == 10
    assert result.classification == "STRONG"


def test_positive_holding_score():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "INFY",
            strength_score=2,
            momentum_score=1,
            volume_score=1,
            signal_score=1,
            confidence=80.0,
        )
    )

    assert result.score == 7
    assert result.classification == "POSITIVE"


def test_neutral_holding_score():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "MARUTI",
            strength_score=0,
            momentum_score=0,
            volume_score=0,
            signal_score=0,
            confidence=50.0,
        )
    )

    assert result.score == 0
    assert result.classification == "NEUTRAL"


def test_weak_holding_score():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "HDFCBANK",
            strength_score=-1,
            momentum_score=-1,
            volume_score=0,
            signal_score=-1,
            confidence=60.0,
        )
    )

    assert result.score == -3
    assert result.classification == "WEAK"


def test_very_weak_holding_score():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "XYZ",
            strength_score=-2,
            momentum_score=-2,
            volume_score=-2,
            signal_score=-2,
            confidence=90.0,
        )
    )

    assert result.score == -10
    assert result.classification == "VERY WEAK"


def test_confidence_is_preserved():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        make_holding(
            "TCS",
            strength_score=2,
            momentum_score=2,
            volume_score=1,
            signal_score=2,
            confidence=87.5,
        )
    )

    assert result.confidence == 87.5


def test_none_holding():
    engine = PortfolioScoringEngine()

    result = engine.analyze(None)

    assert result is None


def test_missing_scores_default_to_zero():
    engine = PortfolioScoringEngine()

    result = engine.analyze(
        {
            "symbol": "TEST",
            "confidence": 50.0,
        }
    )

    assert result.score == 0
    assert result.classification == "NEUTRAL"


def test_original_holding_is_not_mutated():
    engine = PortfolioScoringEngine()

    holding = make_holding(
        "TCS",
        2,
        2,
        2,
        2,
        95.0,
    )

    engine.analyze(holding)

    assert holding["strength_score"] == 2
    assert holding["momentum_score"] == 2
    assert holding["volume_score"] == 2
    assert holding["signal_score"] == 2