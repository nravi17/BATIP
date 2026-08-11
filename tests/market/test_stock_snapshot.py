from batip.market.stock import (
    StockSnapshot,
    StockSnapshotEngine,
)


def make_input(**overrides):
    data = {
        "symbol": "TCS",
        "name": "Tata Consultancy Services",
        "sector": "IT",
        "price": 3500.0,
        "change_percent": 1.5,
        "volume": 1000000,
        "market_bias": "Bullish",
        "confidence": 90.0,
    }

    data.update(overrides)
    return data


def test_stock_snapshot_imports():
    engine = StockSnapshotEngine()

    assert engine is not None


def test_stock_snapshot_returns_snapshot():
    engine = StockSnapshotEngine()

    result = engine.analyze(make_input())

    assert isinstance(result, StockSnapshot)


def test_stock_snapshot_fields():
    engine = StockSnapshotEngine()

    result = engine.analyze(make_input())

    assert result.symbol == "TCS"
    assert result.name == "Tata Consultancy Services"
    assert result.sector == "IT"
    assert result.price == 3500.0
    assert result.change_percent == 1.5
    assert result.volume == 1000000


def test_stock_snapshot_positive_direction():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=1.5)
    )

    assert result.direction == "Bullish"


def test_stock_snapshot_negative_direction():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=-1.5)
    )

    assert result.direction == "Bearish"


def test_stock_snapshot_neutral_direction():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=0.0)
    )

    assert result.direction == "Neutral"


def test_stock_snapshot_positive_score():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=1.5)
    )

    assert result.score == 2


def test_stock_snapshot_small_positive_score():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=0.5)
    )

    assert result.score == 1


def test_stock_snapshot_small_negative_score():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=-0.5)
    )

    assert result.score == -1


def test_stock_snapshot_negative_score():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=-1.5)
    )

    assert result.score == -2


def test_stock_snapshot_neutral_score():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(change_percent=0.0)
    )

    assert result.score == 0


def test_stock_snapshot_preserves_confidence():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(confidence=87.5)
    )

    assert result.confidence == 87.5


def test_stock_snapshot_preserves_market_bias():
    engine = StockSnapshotEngine()

    result = engine.analyze(
        make_input(market_bias="Bearish")
    )

    assert result.market_bias == "Bearish"


def test_stock_snapshot_handles_none():
    engine = StockSnapshotEngine()

    result = engine.analyze(None)

    assert result is None


def test_stock_snapshot_does_not_mutate_input():
    engine = StockSnapshotEngine()

    data = make_input()
    original = dict(data)

    engine.analyze(data)

    assert data == original