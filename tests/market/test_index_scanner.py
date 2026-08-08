from batip.market.index_scanner import IndexScanner
from batip.market.models import (
    IndexSnapshot,
    MarketDirection,
    MarketRegime,
)


def make_index(
    symbol: str,
    change_percent: float,
) -> IndexSnapshot:
    return IndexSnapshot(
        symbol=symbol,
        name=symbol,
        value=1000.0,
        change_percent=change_percent,
    )


def test_positive_index_score():
    scanner = IndexScanner()

    assert scanner.score_index(
        make_index("NIFTY", 1.25)
    ) == 2

    assert scanner.score_index(
        make_index("BANKNIFTY", 0.40)
    ) == 1


def test_negative_index_score():
    scanner = IndexScanner()

    assert scanner.score_index(
        make_index("NIFTY", -1.25)
    ) == -2

    assert scanner.score_index(
        make_index("BANKNIFTY", -0.40)
    ) == -1


def test_neutral_index_score():
    scanner = IndexScanner()

    assert scanner.score_index(
        make_index("NIFTY", 0.0)
    ) == 0


def test_direction_mapping():
    scanner = IndexScanner()

    assert (
        scanner.direction_from_score(2)
        == MarketDirection.BULLISH
    )

    assert (
        scanner.direction_from_score(-2)
        == MarketDirection.BEARISH
    )

    assert (
        scanner.direction_from_score(0)
        == MarketDirection.NEUTRAL
    )


def test_regime_mapping():
    scanner = IndexScanner()

    assert (
        scanner.regime_from_score(6)
        == MarketRegime.STRONG_BULLISH
    )

    assert (
        scanner.regime_from_score(3)
        == MarketRegime.BULLISH
    )

    assert (
        scanner.regime_from_score(0)
        == MarketRegime.NEUTRAL
    )

    assert (
        scanner.regime_from_score(-3)
        == MarketRegime.BEARISH
    )

    assert (
        scanner.regime_from_score(-6)
        == MarketRegime.STRONG_BEARISH
    )


def test_scan_multiple_indices():
    scanner = IndexScanner()

    indices = [
        make_index("NIFTY", 0.80),
        make_index("BANKNIFTY", 1.20),
        make_index("FINNIFTY", -0.30),
        make_index("MIDCPNIFTY", 0.50),
    ]

    result = scanner.scan(indices)

    assert len(result.indices) == 4

    assert result.score == 3

    assert result.regime == MarketRegime.BULLISH

    assert result.strongest_index == "BANKNIFTY"

    assert result.weakest_index == "FINNIFTY"


def test_scan_empty_list():
    scanner = IndexScanner()

    result = scanner.scan([])

    assert result.indices == []
    assert result.score == 0
    assert result.regime == MarketRegime.NEUTRAL