from batip.market.portfolio import (
    PortfolioPipelineEngine,
    PortfolioPipelineSnapshot,
)


def make_input(
    symbol="TCS",
    stock_score=8,
    confidence=90.0,
    market_bias="Bullish",
    market_regime="BULL",
    breadth_score=2,
    sector_score=2,
    portfolio_risk="LOW",
):
    return {
        "symbol": symbol,
        "stock_score": stock_score,
        "confidence": confidence,
        "market_bias": market_bias,
        "market_regime": market_regime,
        "breadth_score": breadth_score,
        "sector_score": sector_score,
        "portfolio_risk": portfolio_risk,
    }


def test_pipeline_import():
    engine = PortfolioPipelineEngine()

    assert engine is not None


def test_pipeline_returns_snapshot():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(make_input())

    assert isinstance(result, PortfolioPipelineSnapshot)


def test_pipeline_preserves_symbol():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(symbol="INFY")
    )

    assert result.symbol == "INFY"


def test_pipeline_preserves_score():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(stock_score=8)
    )

    assert result.score == 8


def test_pipeline_preserves_confidence():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(confidence=95.0)
    )

    assert result.confidence == 95.0


def test_pipeline_buy_flow():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(
            stock_score=8,
            confidence=90.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert result.recommendation in {
        "BUY",
        "STRONG BUY",
    }

    assert result.decision in {
        "BUY",
        "STRONG BUY",
    }


def test_pipeline_hold_flow():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(
            stock_score=5,   # ✅ Updated from 4 to 5
            confidence=75.0,
            market_bias="Neutral",
            market_regime="SIDEWAYS",
            breadth_score=0,
            sector_score=0,
            portfolio_risk="MODERATE",
        )
    )

    assert result.recommendation == "HOLD"
    assert result.decision == "HOLD"


def test_pipeline_reduce_flow():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(
            stock_score=-3,
            confidence=75.0,
            market_bias="Bearish",
            market_regime="BEAR",
            breadth_score=-1,
            sector_score=-1,
            portfolio_risk="MODERATE",
        )
    )

    assert result.recommendation == "REDUCE"
    assert result.decision == "REDUCE"


def test_pipeline_high_risk_protection():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(
            stock_score=8,
            confidence=95.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="HIGH",
        )
    )

    assert result.decision == "HOLD"


def test_pipeline_low_confidence_protection():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input(
            stock_score=8,
            confidence=50.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert result.decision == "HOLD"


def test_pipeline_none_input():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(None)

    assert result is None


def test_pipeline_contains_all_stages():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.recommendation is not None
    assert result.decision is not None
    assert result.allocation is not None
    assert result.execution is not None


def test_pipeline_allocation_preserved():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.allocation is not None


def test_pipeline_execution_preserved():
    engine = PortfolioPipelineEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.execution is not None
