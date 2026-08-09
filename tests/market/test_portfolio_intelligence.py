from batip.market.portfolio import (
    PortfolioIntelligenceEngine,
    PortfolioIntelligenceSnapshot,
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


def test_portfolio_intelligence_imports():
    engine = PortfolioIntelligenceEngine()

    assert engine is not None


def test_strong_portfolio_intelligence():
    engine = PortfolioIntelligenceEngine()

    result = engine.analyze(
        make_input(
            symbol="TCS",
            stock_score=8,
            confidence=95.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert isinstance(result, PortfolioIntelligenceSnapshot)
    assert result.symbol == "TCS"


def test_bearish_environment():
    engine = PortfolioIntelligenceEngine()

    result = engine.analyze(
        make_input(
            symbol="INFY",
            stock_score=3,
            confidence=75.0,
            market_bias="Bearish",
            market_regime="BEAR",
            breadth_score=-2,
            sector_score=-2,
            portfolio_risk="HIGH",
        )
    )

    assert isinstance(result, PortfolioIntelligenceSnapshot)
    assert result.symbol == "INFY"


def test_none_input():
    engine = PortfolioIntelligenceEngine()

    result = engine.analyze(None)

    assert result is None