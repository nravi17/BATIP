from batip.market.sector import (
    SectorScanner,
    SectorSnapshot,
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


def test_strong_bullish_sector_score():
    scanner = SectorScanner()

    assert scanner.score_sector(1.25) == 2


def test_bullish_sector_score():
    scanner = SectorScanner()

    assert scanner.score_sector(0.45) == 1


def test_neutral_sector_score():
    scanner = SectorScanner()

    assert scanner.score_sector(0.0) == 0


def test_bearish_sector_score():
    scanner = SectorScanner()

    assert scanner.score_sector(-0.45) == -1


def test_strong_bearish_sector_score():
    scanner = SectorScanner()

    assert scanner.score_sector(-1.25) == -2


def test_direction_mapping():
    scanner = SectorScanner()

    assert scanner.direction_from_score(2) == "Bullish"
    assert scanner.direction_from_score(1) == "Bullish"
    assert scanner.direction_from_score(0) == "Neutral"
    assert scanner.direction_from_score(-1) == "Bearish"
    assert scanner.direction_from_score(-2) == "Bearish"


def test_sector_analysis_ranks_sectors():
    scanner = SectorScanner()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.80),
        make_sector("AUTO", -0.30),
        make_sector("PHARMA", -1.10),
    ]

    result = scanner.analyze(sectors)

    assert len(result) == 4

    assert result[0].symbol == "IT"
    assert result[1].symbol == "BANK"
    assert result[2].symbol == "AUTO"
    assert result[3].symbol == "PHARMA"

    assert result[0].score == 2
    assert result[0].direction == "Bullish"

    assert result[-1].score == -2
    assert result[-1].direction == "Bearish"


def test_strongest_sector():
    scanner = SectorScanner()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.80),
        make_sector("AUTO", -0.30),
    ]

    result = scanner.analyze(sectors)

    strongest = scanner.strongest(result)

    assert strongest is not None
    assert strongest.symbol == "IT"


def test_weakest_sector():
    scanner = SectorScanner()

    sectors = [
        make_sector("IT", 1.20),
        make_sector("BANK", 0.80),
        make_sector("AUTO", -0.30),
    ]

    result = scanner.analyze(sectors)

    weakest = scanner.weakest(result)

    assert weakest is not None
    assert weakest.symbol == "AUTO"


def test_empty_sector_list():
    scanner = SectorScanner()

    result = scanner.analyze([])

    assert result == []
    assert scanner.strongest(result) is None
    assert scanner.weakest(result) is None