from batip.market.market import MarketIntelligenceEngine
from batip.market.sector import SectorSnapshot
from batip.market.stock import StockIntelligenceSnapshot


def make_sector(symbol, change_percent, score):
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


def make_stock(symbol, score, recommendation, confidence):
    return StockIntelligenceSnapshot(
        symbol=symbol,
        name=symbol,
        sector="IT",
        sector_score=0,
        strength_score=score,
        momentum_score=0,
        volume_score=0,
        signal_score=0,
        total_score=score,
        direction=(
            "Bullish"
            if score > 0
            else "Bearish"
            if score < 0
            else "Neutral"
        ),
        recommendation=recommendation,
        confidence=confidence,
    )


def test_market_intelligence_accepts_breadth():
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

    result = engine.analyze(
        sectors,
        stocks,
        breadth_advances=700,
        breadth_declines=200,
        breadth_unchanged=100,
    )

    assert result is not None