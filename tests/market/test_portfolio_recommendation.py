from batip.market.portfolio import (
    PortfolioRecommendationEngine,
    PortfolioRecommendationSnapshot,
)


def make_input(
    symbol="TCS",
    stock_score=8,
    confidence=90.0,
    market_bias="Bullish",
    market_regime="BULL",
    breadth_score=2,
    sector_score=2,
    portfolio_score=8,
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
        "portfolio_score": portfolio_score,
        "portfolio_risk": portfolio_risk,
    }


def test_recommendation_imports():
    engine = PortfolioRecommendationEngine()

    assert engine is not None


def test_strong_buy_recommendation():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=10,
            confidence=95.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert isinstance(result, PortfolioRecommendationSnapshot)
    assert result.symbol == "TCS"
    assert result.action == "STRONG BUY"


def test_buy_recommendation():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=7,
            confidence=85.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=1,
            sector_score=1,
            portfolio_risk="LOW",
        )
    )

    assert result.action == "BUY"


def test_hold_recommendation():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=3,
            confidence=70.0,
            market_bias="Neutral",
            market_regime="SIDEWAYS",
            breadth_score=0,
            sector_score=0,
            portfolio_risk="LOW",
        )
    )

    assert result.action == "HOLD"


def test_watch_recommendation():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=1,
            confidence=55.0,
            market_bias="Neutral",
            market_regime="SIDEWAYS",
            breadth_score=0,
            sector_score=0,
            portfolio_risk="LOW",
        )
    )

    assert result.action == "WATCH"


def test_reduce_recommendation():
    engine = PortfolioRecommendationEngine()

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

    assert result.action == "REDUCE"


def test_exit_recommendation():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=-8,
            confidence=90.0,
            market_bias="Bearish",
            market_regime="BEAR",
            breadth_score=-2,
            sector_score=-2,
            portfolio_risk="HIGH",
        )
    )

    assert result.action == "EXIT"


def test_high_risk_overrides_buy_signal():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=10,
            confidence=95.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="HIGH",
        )
    )

    assert result.action != "STRONG BUY"
    assert result.action in {"HOLD", "REDUCE"}


def test_bearish_market_reduces_bullish_signal():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=8,
            confidence=90.0,
            market_bias="Bearish",
            market_regime="BEAR",
            breadth_score=-2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert result.action in {"HOLD", "WATCH"}


def test_bullish_market_supports_positive_signal():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=7,
            confidence=90.0,
            market_bias="Bullish",
            market_regime="BULL",
            breadth_score=2,
            sector_score=2,
            portfolio_risk="LOW",
        )
    )

    assert result.action == "BUY"


def test_confidence_is_preserved():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            stock_score=7,
            confidence=82.5,
        )
    )

    assert result.confidence == 82.5


def test_symbol_is_preserved():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(
        make_input(
            symbol="HDFCBANK",
            stock_score=3,
        )
    )

    assert result.symbol == "HDFCBANK"


def test_none_input():
    engine = PortfolioRecommendationEngine()

    result = engine.analyze(None)

    assert result is None