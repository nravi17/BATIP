from batip.market.stock import (
    StockIntelligenceEngine,
    StockIntelligenceSnapshot,
)


def test_strong_buy_intelligence():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TCS",
        name="TCS",
        sector="IT",
        sector_score=2,
        strength_score=2,
        momentum_score=2,
        volume_score=2,
        signal_score=2,
    )

    assert isinstance(result, StockIntelligenceSnapshot)

    assert result.symbol == "TCS"
    assert result.sector == "IT"

    assert result.total_score == 10
    assert result.direction == "Bullish"
    assert result.recommendation == "STRONG BUY"


def test_buy_intelligence():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="INFY",
        name="Infosys",
        sector="IT",
        sector_score=1,
        strength_score=1,
        momentum_score=1,
        volume_score=1,
        signal_score=1,
    )

    assert result.total_score == 5
    assert result.direction == "Bullish"
    assert result.recommendation == "BUY"


def test_neutral_intelligence():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TEST",
        name="Test Stock",
        sector="AUTO",
        sector_score=0,
        strength_score=0,
        momentum_score=0,
        volume_score=0,
        signal_score=0,
    )

    assert result.total_score == 0
    assert result.direction == "Neutral"
    assert result.recommendation == "WATCH"


def test_sell_intelligence():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TEST",
        name="Test Stock",
        sector="AUTO",
        sector_score=-1,
        strength_score=-1,
        momentum_score=-1,
        volume_score=-1,
        signal_score=-1,
    )

    assert result.total_score == -5
    assert result.direction == "Bearish"
    assert result.recommendation == "SELL"


def test_strong_sell_intelligence():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TEST",
        name="Test Stock",
        sector="AUTO",
        sector_score=-2,
        strength_score=-2,
        momentum_score=-2,
        volume_score=-2,
        signal_score=-2,
    )

    assert result.total_score == -10
    assert result.direction == "Bearish"
    assert result.recommendation == "STRONG SELL"


def test_confidence_is_high_for_aligned_signals():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TCS",
        name="TCS",
        sector="IT",
        sector_score=2,
        strength_score=2,
        momentum_score=2,
        volume_score=2,
        signal_score=2,
    )

    assert result.confidence >= 80


def test_confidence_is_low_for_mixed_signals():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TEST",
        name="Test Stock",
        sector="IT",
        sector_score=2,
        strength_score=-2,
        momentum_score=2,
        volume_score=-2,
        signal_score=0,
    )

    assert result.confidence < 80


def test_rank_stocks():
    engine = StockIntelligenceEngine()

    stocks = [
        engine.analyze(
            symbol="A",
            name="Stock A",
            sector="IT",
            sector_score=2,
            strength_score=2,
            momentum_score=2,
            volume_score=2,
            signal_score=2,
        ),
        engine.analyze(
            symbol="B",
            name="Stock B",
            sector="BANK",
            sector_score=1,
            strength_score=1,
            momentum_score=1,
            volume_score=1,
            signal_score=1,
        ),
        engine.analyze(
            symbol="C",
            name="Stock C",
            sector="AUTO",
            sector_score=-2,
            strength_score=-2,
            momentum_score=-2,
            volume_score=-2,
            signal_score=-2,
        ),
    ]

    result = engine.rank(stocks)

    assert [stock.symbol for stock in result] == [
        "A",
        "B",
        "C",
    ]


def test_empty_rank():
    engine = StockIntelligenceEngine()

    assert engine.rank([]) == []


def test_original_snapshot_is_not_mutated():
    engine = StockIntelligenceEngine()

    result = engine.analyze(
        symbol="TCS",
        name="TCS",
        sector="IT",
        sector_score=2,
        strength_score=2,
        momentum_score=2,
        volume_score=2,
        signal_score=2,
    )

    assert result.total_score == 10