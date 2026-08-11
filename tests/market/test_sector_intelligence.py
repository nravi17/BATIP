from batip.market.sector import (
    SectorIntelligenceEngine,
    SectorIntelligenceSnapshot,
    SectorSnapshot,
)


def make_sector(
    symbol,
    name,
    change_percent,
    score=0,
):
    return SectorSnapshot(
        symbol=symbol,
        name=name,
        change_percent=change_percent,
        score=score,
    )


def make_current():
    return [
        make_sector("IT", "IT", 1.5),
        make_sector("BANK", "Banking", 0.8),
        make_sector("AUTO", "Auto", -1.2),
        make_sector("FMCG", "FMCG", 0.0),
    ]


def make_previous():
    return [
        make_sector("IT", "IT", 1.0),
        make_sector("BANK", "Banking", 0.2),
        make_sector("AUTO", "Auto", -0.5),
        make_sector("FMCG", "FMCG", 0.0),
    ]


def test_sector_intelligence_imports():
    engine = SectorIntelligenceEngine()

    assert engine is not None


def test_sector_intelligence_returns_snapshot():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert isinstance(result, SectorIntelligenceSnapshot)


def test_sector_intelligence_preserves_sectors():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert len(result.sectors) == 4


def test_sector_intelligence_calculates_strength():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert result.total_score == 1
    assert result.average_score == 0.25


def test_sector_intelligence_identifies_strongest():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert result.strongest_sector == "IT"


def test_sector_intelligence_identifies_weakest():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert result.weakest_sector == "AUTO"


def test_sector_intelligence_counts_direction():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert result.bullish_count == 2
    assert result.bearish_count == 1
    assert result.neutral_count == 1


def test_sector_intelligence_bias():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(make_current(), make_previous())

    assert result.sector_bias == "Bullish"


def test_sector_intelligence_rotation_leaders():
    engine = SectorIntelligenceEngine()

    current = [
        make_sector("IT", "IT", 1.5),
    ]

    previous = [
        make_sector("IT", "IT", 1.2),
    ]

    result = engine.analyze(current, previous)

    assert result.rotation_leaders == ["IT"]


def test_sector_intelligence_rotation_improving():
    engine = SectorIntelligenceEngine()

    current = [
        make_sector("BANK", "Banking", 0.8),
    ]

    previous = [
        make_sector("BANK", "Banking", -0.8),
    ]

    result = engine.analyze(current, previous)

    assert result.rotation_improving == ["BANK"]


def test_sector_intelligence_rotation_weakening():
    engine = SectorIntelligenceEngine()

    current = [
        make_sector("AUTO", "Auto", -0.5),
    ]

    previous = [
        make_sector("AUTO", "Auto", 0.5),
    ]

    result = engine.analyze(current, previous)

    assert result.rotation_weakening == ["AUTO"]


def test_sector_intelligence_confidence_with_history():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(
        make_current(),
        make_previous(),
    )

    assert result.confidence == 100.0


def test_sector_intelligence_confidence_without_history():
    engine = SectorIntelligenceEngine()

    result = engine.analyze(
        make_current(),
        [],
    )

    assert result.confidence == 70.0


def test_sector_intelligence_empty_input():
    engine = SectorIntelligenceEngine()

    result = engine.analyze([], [])

    assert result.sectors == []
    assert result.total_score == 0
    assert result.sector_bias == "Neutral"
    assert result.confidence == 0.0


def test_sector_intelligence_does_not_mutate_input():
    engine = SectorIntelligenceEngine()

    current = make_current()
    previous = make_previous()

    current_original = list(current)
    previous_original = list(previous)

    engine.analyze(current, previous)

    assert current == current_original
    assert previous == previous_original