from batip.market.sector import (
    SectorIntelligenceSnapshot,
    SectorSnapshotEngine,
)


def make_input(**overrides):
    data = {
        "sector": "IT",
        "breadth_score": 2,
        "momentum_score": 6,
        "market_bias": "Bullish",
        "confidence": 90.0,
    }

    data.update(overrides)
    return data


def test_sector_snapshot_imports():
    engine = SectorSnapshotEngine()

    assert engine is not None


def test_sector_snapshot_returns_snapshot():
    engine = SectorSnapshotEngine()

    result = engine.analyze(make_input())

    assert isinstance(result, SectorIntelligenceSnapshot)


def test_sector_snapshot_preserves_sector():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(sector="BANKING")
    )

    assert result.sector == "BANKING"


def test_sector_snapshot_calculates_score():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=2,
            momentum_score=6,
        )
    )

    assert result.score == 8


def test_sector_snapshot_strong_classification():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=4,
            momentum_score=5,
        )
    )

    assert result.classification == "STRONG"


def test_sector_snapshot_positive_classification():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=1,
            momentum_score=4,
        )
    )

    assert result.classification == "POSITIVE"


def test_sector_snapshot_neutral_classification():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=0,
            momentum_score=0,
        )
    )

    assert result.classification == "NEUTRAL"


def test_sector_snapshot_weak_classification():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=-1,
            momentum_score=-2,
        )
    )

    assert result.classification == "WEAK"


def test_sector_snapshot_very_weak_classification():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(
            breadth_score=-4,
            momentum_score=-5,
        )
    )

    assert result.classification == "VERY WEAK"


def test_sector_snapshot_preserves_market_bias():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(market_bias="Bearish")
    )

    assert result.market_bias == "Bearish"


def test_sector_snapshot_preserves_confidence():
    engine = SectorSnapshotEngine()

    result = engine.analyze(
        make_input(confidence=87.5)
    )

    assert result.confidence == 87.5


def test_sector_snapshot_none_input():
    engine = SectorSnapshotEngine()

    assert engine.analyze(None) is None


def test_sector_snapshot_does_not_mutate_input():
    engine = SectorSnapshotEngine()

    data = make_input()

    original = data.copy()

    engine.analyze(data)

    assert data == original
