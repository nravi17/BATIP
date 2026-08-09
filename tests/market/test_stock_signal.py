from batip.market.stock import (
    StockSignalEngine,
    StockSignalSnapshot,
)


def make_signal(
    symbol: str,
    price_score: int,
    momentum_score: int,
    volume_score: int,
    sector_score: int,
    liquidity_score: int,
) -> StockSignalSnapshot:
    return StockSignalSnapshot(
        symbol=symbol,
        price_score=price_score,
        momentum_score=momentum_score,
        volume_score=volume_score,
        sector_score=sector_score,
        liquidity_score=liquidity_score,
    )


def test_strong_buy_signal():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "TCS",
            price_score=2,
            momentum_score=2,
            volume_score=2,
            sector_score=2,
            liquidity_score=2,
        )
    )

    assert result.total_score == 10
    assert result.direction == "Bullish"
    assert result.signal == "STRONG BUY"
    assert result.confidence == "High"


def test_buy_signal():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "INFY",
            price_score=1,
            momentum_score=1,
            volume_score=1,
            sector_score=1,
            liquidity_score=1,
        )
    )

    assert result.total_score == 5
    assert result.direction == "Bullish"
    assert result.signal == "BUY"
    assert result.confidence == "High"


def test_watch_signal():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "RELIANCE",
            price_score=1,
            momentum_score=-1,
            volume_score=0,
            sector_score=0,
            liquidity_score=0,
        )
    )

    assert result.total_score == 0
    assert result.direction == "Neutral"
    assert result.signal == "WATCH"


def test_sell_signal():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "MARUTI",
            price_score=-1,
            momentum_score=-1,
            volume_score=-1,
            sector_score=-1,
            liquidity_score=-1,
        )
    )

    assert result.total_score == -5
    assert result.direction == "Bearish"
    assert result.signal == "SELL"
    assert result.confidence == "High"


def test_strong_sell_signal():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "XYZ",
            price_score=-2,
            momentum_score=-2,
            volume_score=-2,
            sector_score=-2,
            liquidity_score=-2,
        )
    )

    assert result.total_score == -10
    assert result.direction == "Bearish"
    assert result.signal == "STRONG SELL"
    assert result.confidence == "High"


def test_direction_mapping():
    engine = StockSignalEngine()

    assert engine.direction_from_score(10) == "Bullish"
    assert engine.direction_from_score(5) == "Bullish"
    assert engine.direction_from_score(0) == "Neutral"
    assert engine.direction_from_score(-5) == "Bearish"
    assert engine.direction_from_score(-10) == "Bearish"


def test_signal_mapping():
    engine = StockSignalEngine()

    assert engine.signal_from_score(10) == "STRONG BUY"
    assert engine.signal_from_score(7) == "STRONG BUY"
    assert engine.signal_from_score(5) == "BUY"
    assert engine.signal_from_score(1) == "WATCH"
    assert engine.signal_from_score(0) == "WATCH"
    assert engine.signal_from_score(-1) == "WATCH"
    assert engine.signal_from_score(-5) == "SELL"
    assert engine.signal_from_score(-7) == "STRONG SELL"
    assert engine.signal_from_score(-10) == "STRONG SELL"


def test_confidence_mapping():
    engine = StockSignalEngine()

    assert engine.confidence_from_score(10) == "High"
    assert engine.confidence_from_score(5) == "High"
    assert engine.confidence_from_score(3) == "Medium"
    assert engine.confidence_from_score(1) == "Low"
    assert engine.confidence_from_score(0) == "Low"
    assert engine.confidence_from_score(-3) == "Medium"
    assert engine.confidence_from_score(-5) == "High"
    assert engine.confidence_from_score(-10) == "High"


def test_component_scores_are_preserved():
    engine = StockSignalEngine()

    result = engine.analyze(
        make_signal(
            "HDFCBANK",
            price_score=2,
            momentum_score=1,
            volume_score=0,
            sector_score=2,
            liquidity_score=1,
        )
    )

    assert result.symbol == "HDFCBANK"
    assert result.price_score == 2
    assert result.momentum_score == 1
    assert result.volume_score == 0
    assert result.sector_score == 2
    assert result.liquidity_score == 1
    assert result.total_score == 6


def test_none_signal_is_rejected():
    engine = StockSignalEngine()

    try:
        engine.analyze(None)
        assert False
    except ValueError:
        assert True