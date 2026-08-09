from batip.market.sector import (
    SectorSnapshot,
    SectorStrengthEngine,
)


def make_sector(
    symbol: str,
    change_percent: float,
) -> SectorSnapshot:
    return SectorSnapshot(
        symbol=symbol,
        name=symbol,
        change_percent=change_percent,
    )


def test_strong_bullish_sector_strength():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 1.50),
        make_sector("BANK", 1.20),
        make_sector("AUTO", 0.80),
    ]

    result = engine.analyze(sectors)

    assert result.bias == "Strong Bullish"
    assert result.bullish_count == 3
    assert result.bearish_count == 0
    assert result.neutral_count == 0
    assert result.total_score == 5
    assert result.strongest_sector == "IT"


def test_bullish_sector_strength():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 0.80),
        make_sector("BANK", 0.40),
        make_sector("PHARMA", -0.30),
    ]

    result = engine.analyze(sectors)

    assert result.bias == "Bullish"
    assert result.bullish_count == 2
    assert result.bearish_count == 1
    assert result.total_score == 1


def test_neutral_sector_strength():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 0.20),
        make_sector("BANK", -0.20),
    ]

    result = engine.analyze(sectors)

    assert result.bias == "Neutral"
    assert result.total_score == 0


def test_strong_bearish_sector_strength():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("PHARMA", -1.50),
        make_sector("METAL", -1.20),
        make_sector("AUTO", -0.80),
    ]

    result = engine.analyze(sectors)

    assert result.bias == "Strong Bearish"
    assert result.bullish_count == 0
    assert result.bearish_count == 3
    assert result.neutral_count == 0
    assert result.total_score == -5
    assert result.weakest_sector == "PHARMA"


def test_sector_counts():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.50),
        make_sector("AUTO", 0.00),
        make_sector("PHARMA", -0.40),
        make_sector("METAL", -1.20),
    ]

    result = engine.analyze(sectors)

    assert result.bullish_count == 2
    assert result.bearish_count == 2
    assert result.neutral_count == 1


def test_strongest_and_weakest_sector():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.80),
        make_sector("AUTO", -0.30),
        make_sector("PHARMA", -1.10),
    ]

    result = engine.analyze(sectors)

    assert result.strongest_sector == "IT"
    assert result.weakest_sector == "PHARMA"


def test_average_score():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.80),
        make_sector("AUTO", -0.30),
        make_sector("PHARMA", -1.10),
    ]

    result = engine.analyze(sectors)

    assert result.total_score == 0
    assert result.average_score == 0.0


def test_empty_sector_list():
    engine = SectorStrengthEngine()

    result = engine.analyze([])

    assert result.sectors == []
    assert result.strongest_sector is None
    assert result.weakest_sector is None
    assert result.bullish_count == 0
    assert result.bearish_count == 0
    assert result.neutral_count == 0
    assert result.total_score == 0
    assert result.average_score == 0.0
    assert result.bias == "Neutral"


def test_none_entries_are_ignored():
    engine = SectorStrengthEngine()

    sectors = [
        make_sector("IT", 1.20),
        None,
        make_sector("PHARMA", -1.20),
    ]

    result = engine.analyze(sectors)

    assert len(result.sectors) == 2
    assert result.bullish_count == 1
    assert result.bearish_count == 1
    assert result.total_score == 0
    assert result.bias == "Neutral"


def test_sector_snapshots_are_not_mutated():
    engine = SectorStrengthEngine()

    original = make_sector("IT", 1.20)

    engine.analyze([original])

    assert original.score == 0
    assert original.direction == "Neutral"