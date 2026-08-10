from batip.market.portfolio import (
    PortfolioDecisionEngine,
    PortfolioDecisionSnapshot,
)


def make_input(
    symbol: str,
    score: int,
    classification: str,
    risk: str,
    action: str,
    confidence: float,
):
    return {
        "symbol": symbol,
        "score": score,
        "classification": classification,
        "risk": risk,
        "action": action,
        "confidence": confidence,
    }


def test_portfolio_decision_imports():
    engine = PortfolioDecisionEngine()

    assert engine is not None


def test_strong_buy_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "TCS",
            score=10,
            classification="STRONG",
            risk="LOW",
            action="STRONG BUY",
            confidence=95.0,
        )
    )

    assert isinstance(result, PortfolioDecisionSnapshot)
    assert result.symbol == "TCS"
    assert result.decision == "STRONG BUY"
    assert result.confidence == 95.0


def test_buy_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "INFY",
            score=7,
            classification="POSITIVE",
            risk="LOW",
            action="BUY",
            confidence=85.0,
        )
    )

    assert result.decision == "BUY"


def test_hold_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "MARUTI",
            score=2,
            classification="NEUTRAL",
            risk="MODERATE",
            action="HOLD",
            confidence=65.0,
        )
    )

    assert result.decision == "HOLD"


def test_watch_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "ITC",
            score=0,
            classification="NEUTRAL",
            risk="MODERATE",
            action="WATCH",
            confidence=50.0,
        )
    )

    assert result.decision == "WATCH"


def test_reduce_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "HDFCBANK",
            score=-3,
            classification="WEAK",
            risk="MODERATE",
            action="REDUCE",
            confidence=70.0,
        )
    )

    assert result.decision == "REDUCE"


def test_exit_decision():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "XYZ",
            score=-10,
            classification="VERY WEAK",
            risk="HIGH",
            action="EXIT",
            confidence=90.0,
        )
    )

    assert result.decision == "EXIT"


def test_high_risk_downgrades_strong_buy():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "TCS",
            score=10,
            classification="STRONG",
            risk="HIGH",
            action="STRONG BUY",
            confidence=95.0,
        )
    )

    assert result.decision == "HOLD"


def test_high_risk_downgrades_buy():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        make_input(
            "INFY",
            score=7,
            classification="POSITIVE",
            risk="HIGH",
            action="BUY",
            confidence=85.0,
        )
    )

    assert result.decision == "HOLD"


def test_none_input():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(None)

    assert result is None


def test_missing_fields_use_safe_defaults():
    engine = PortfolioDecisionEngine()

    result = engine.analyze(
        {
            "symbol": "TEST",
        }
    )

    assert isinstance(result, PortfolioDecisionSnapshot)
    assert result.decision == "WATCH"