from batip.market.portfolio import (
    PortfolioDecisionEngine,
    PortfolioDecisionSnapshot,
)


def make_input(
    action: str,
    score: int,
    risk: str,
    confidence: float,
):
    return {
        "action": action,
        "score": score,
        "risk": risk,
        "confidence": confidence,
    }


def test_portfolio_decision_imports():
    engine = PortfolioDecisionEngine()

    assert engine is not None


def test_buy_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="BUY",
            score=8,
            risk="LOW",
            confidence=90.0,
        )
    )

    assert isinstance(result, PortfolioDecisionSnapshot)
    assert result.action == "BUY"


def test_hold_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="HOLD",
            score=4,
            risk="MODERATE",
            confidence=75.0,
        )
    )

    assert result.action == "HOLD"


def test_reduce_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="REDUCE",
            score=-3,
            risk="MODERATE",
            confidence=70.0,
        )
    )

    assert result.action == "REDUCE"


def test_exit_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="EXIT",
            score=-9,
            risk="HIGH",
            confidence=90.0,
        )
    )

    assert result.action == "EXIT"


def test_high_risk_blocks_buy():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="BUY",
            score=8,
            risk="HIGH",
            confidence=95.0,
        )
    )

    assert result.action == "HOLD"


def test_low_confidence_blocks_buy():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="BUY",
            score=8,
            risk="LOW",
            confidence=50.0,
        )
    )

    assert result.action == "HOLD"


def test_strong_buy_is_preserved_when_conditions_are_good():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="STRONG BUY",
            score=10,
            risk="LOW",
            confidence=95.0,
        )
    )

    assert result.action == "STRONG BUY"


def test_none_input():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(None)

    assert result is None


def test_confidence_is_preserved():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="BUY",
            score=8,
            risk="LOW",
            confidence=87.5,
        )
    )

    assert result.confidence == 87.5


def test_score_is_preserved():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            action="BUY",
            score=8,
            risk="LOW",
            confidence=90.0,
        )
    )

    assert result.score == 8