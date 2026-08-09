from batip.market.sector import SectorSnapshot
from batip.market.stock import StockIntelligenceSnapshot
from batip.market.market import (
    MarketIntelligenceEngine,
    MarketIntelligenceSnapshot,
)


def make_sector(
    symbol: str,
    change_percent: float,
    score: int,
) -> SectorSnapshot:
    return SectorSnapshot(
        symbol=symbol,
        name=symbol,
        change_percent=change_percent,
        score=score,
        direction=(
            "Bullish"
            if score > 0
            else "Bearish"
            if score < 0
            else "Neutral"
        ),
    )


def make_stock(
    symbol: str,
    total_score: int,
    recommendation: str,
    confidence: float,
) -> StockIntelligenceSnapshot:
    return StockIntelligenceSnapshot(
        symbol=symbol,
        name=symbol,
        sector="IT",
        sector_score=1,
        strength_score=1,
        momentum_score=1,
        volume_score=1,
        signal_score=1,
        total_score=total_score,
        direction="Bullish" if total_score > 0 else "Bearish",
        recommendation=recommendation,
        confidence=confidence,
    )


def test_market_intelligence_import():
    engine = MarketIntelligenceEngine()

    assert engine is not None


def test_bullish_market():
    engine = MarketIntelligenceEngine()

    sectors = [
        make_sector("IT", 1.50, 2),
        make_sector("BANK", 0.80, 1),
        make_sector("AUTO", 0.40, 1),
    ]

    stocks = [
        make_stock("TCS", 8, "STRONG BUY", 90.0),
        make_stock("INFY", 6, "BUY", 85.0),
    ]

    result = engine.analyze(sectors, stocks)

    assert isinstance(result, MarketIntelligenceSnapshot)
    assert result.market_bias == "Bullish"
    assert result.strongest_sector == "IT"
    assert result.top_stock == "TCS"


def test_bearish_market():
    engine = MarketIntelligenceEngine()

    sectors = [
        make_sector("IT", -1.50, -2),
        make_sector("BANK", -0.80, -1),
        make_sector("AUTO", -0.40, -1),
    ]

    stocks = [
        make_stock("TCS", -8, "STRONG SELL", 90.0),
        make_stock("INFY", -6, "SELL", 85.0),
    ]

    result = engine.analyze(sectors, stocks)

    assert result.market_bias == "Bearish"
    assert result.weakest_sector == "IT"


def test_neutral_market():
    engine = MarketIntelligenceEngine()

    sectors = [
        make_sector("IT", 0.0, 0),
        make_sector("BANK", 0.0, 0),
    ]

    stocks = [
        make_stock("TCS", 0, "WATCH", 50.0),
    ]

    result = engine.analyze(sectors, stocks)

    assert result.market_bias == "Neutral"


def test_top_stocks_are_ranked():
    engine = MarketIntelligenceEngine()

    sectors = [
        make_sector("IT", 1.0, 2),
    ]

    stocks = [
        make_stock("INFY", 5, "BUY", 80.0),
        make_stock("TCS", 9, "STRONG BUY", 95.0),
        make_stock("WIPRO", 2, "BUY", 70.0),
    ]

    result = engine.analyze(sectors, stocks)

    assert result.top_stock == "TCS"


def test_empty_market():
    engine = MarketIntelligenceEngine()

    result = engine.analyze([], [])

    assert result.market_bias == "Neutral"
    assert result.strongest_sector is None
    assert result.weakest_sector is None
    assert result.top_stock is None