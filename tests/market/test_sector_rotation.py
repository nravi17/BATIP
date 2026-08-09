from batip.market.sector import (
    SectorRotation,
    SectorRotationEngine,
    SectorRotationSnapshot,
    SectorSnapshot,
)


def make_sector(
    symbol: str,
    change_percent: float,
    score: int = 0,
) -> SectorSnapshot:
    return SectorSnapshot(
        symbol=symbol,
        name=symbol,
        change_percent=change_percent,
        score=score,
    )


def test_leading_sector():
    engine = SectorRotationEngine()

    current = make_sector("IT", 1.50, 2)
    previous = make_sector("IT", 1.00, 2)

    result = engine.classify(current, previous)

    assert result == SectorRotation.LEADING


def test_improving_sector():
    engine = SectorRotationEngine()

    current = make_sector("BANK", 0.50, 1)
    previous = make_sector("BANK", -0.20, -1)

    result = engine.classify(current, previous)

    assert result == SectorRotation.IMPROVING


def test_emerging_sector():
    engine = SectorRotationEngine()

    current = make_sector("PHARMA", 0.10, 0)
    previous = make_sector("PHARMA", -0.10, -1)

    result = engine.classify(current, previous)

    assert result == SectorRotation.EMERGING


def test_weakening_sector():
    engine = SectorRotationEngine()

    current = make_sector("AUTO", -0.30, -1)
    previous = make_sector("AUTO", 0.50, 1)

    result = engine.classify(current, previous)

    assert result == SectorRotation.WEAKENING


def test_lagging_sector():
    engine = SectorRotationEngine()

    current = make_sector("REALTY", -1.50, -2)
    previous = make_sector("REALTY", -1.00, -2)

    result = engine.classify(current, previous)

    assert result == SectorRotation.LAGGING


def test_neutral_sector():
    engine = SectorRotationEngine()

    current = make_sector("FMCG", 0.05, 0)
    previous = make_sector("FMCG", 0.05, 0)

    result = engine.classify(current, previous)

    assert result == SectorRotation.NEUTRAL


def test_score_change():
    engine = SectorRotationEngine()

    current = make_sector("BANK", 0.80, 2)
    previous = make_sector("BANK", 0.20, 1)

    result = engine.score_change(current, previous)

    assert result == 1


def test_rotation_analysis():
    engine = SectorRotationEngine()

    current = [
        make_sector("IT", 1.50, 2),
        make_sector("BANK", 0.60, 1),
        make_sector("AUTO", -0.30, -1),
        make_sector("REALTY", -1.40, -2),
    ]

    previous = [
        make_sector("IT", 1.00, 2),
        make_sector("BANK", -0.20, -1),
        make_sector("AUTO", 0.40, 1),
        make_sector("REALTY", -1.00, -2),
    ]

    result = engine.analyze(current, previous)

    assert isinstance(result, SectorRotationSnapshot)

    assert len(result.sectors) == 4

    assert result.sectors[0].symbol == "IT"
    assert result.sectors[0].rotation == SectorRotation.LEADING

    assert result.sectors[1].symbol == "BANK"
    assert result.sectors[1].rotation == SectorRotation.IMPROVING

    assert result.sectors[2].symbol == "AUTO"
    assert result.sectors[2].rotation == SectorRotation.WEAKENING

    assert result.sectors[3].symbol == "REALTY"
    assert result.sectors[3].rotation == SectorRotation.LAGGING


def test_empty_rotation_analysis():
    engine = SectorRotationEngine()

    result = engine.analyze([], [])

    assert isinstance(result, SectorRotationSnapshot)
    assert result.sectors == []


def test_missing_previous_sector():
    engine = SectorRotationEngine()

    current = [
        make_sector("IT", 1.20, 2),
    ]

    result = engine.analyze(current, [])

    assert len(result.sectors) == 1
    assert result.sectors[0].symbol == "IT"