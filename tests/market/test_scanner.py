from batip.market.models import (
    IndexSnapshot,
    MarketBreadth,
    MarketDataStatus,
    MarketDirection,
    MarketRegime,
)
from batip.market.scanner import MarketScanner


def make_index(
    symbol: str,
    change_percent: float,
    direction: MarketDirection,
    score: int,
    status: MarketDataStatus = MarketDataStatus.LIVE,
) -> IndexSnapshot:
    return IndexSnapshot(
        symbol=symbol,
        name=symbol,
        value=100.0,
        change_percent=change_percent,
        direction=direction,
        score=score,
        status=status,
    )


def make_breadth(
    direction: MarketDirection,
    score: float = 2.0,
    status: MarketDataStatus = MarketDataStatus.LIVE,
) -> MarketBreadth:
    return MarketBreadth(
        advances=100,
        declines=50,
        unchanged=10,
        advance_decline_ratio=2.0,
        breadth_score=score,
        direction=direction,
        status=status,
    )


def test_empty_market_is_neutral_and_unavailable():
    scanner = MarketScanner()

    result = scanner.scan()

    assert result.indices == []
    assert result.breadth is None
    assert result.regime == MarketRegime.NEUTRAL
    assert result.score == 0
    assert result.strongest_index is None
    assert result.weakest_index is None
    assert result.status == MarketDataStatus.UNAVAILABLE
    assert result.reasons


def test_bullish_market():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.2,
            MarketDirection.BULLISH,
            1,
        ),
        make_index(
            "BANKNIFTY",
            1.8,
            MarketDirection.BULLISH,
            1,
        ),
    ]

    breadth = make_breadth(
        MarketDirection.BULLISH,
    )

    result = scanner.scan(
        indices,
        breadth,
        timestamp="2026-08-09T10:00:00+00:00",
    )

    assert result.regime == MarketRegime.STRONG_BULLISH
    assert result.score == 6
    assert result.strongest_index == "BANKNIFTY"
    assert result.weakest_index == "NIFTY"
    assert result.status == MarketDataStatus.LIVE
    assert result.timestamp == "2026-08-09T10:00:00+00:00"


def test_bearish_market():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            -1.2,
            MarketDirection.BEARISH,
            -1,
        ),
        make_index(
            "BANKNIFTY",
            -1.8,
            MarketDirection.BEARISH,
            -1,
        ),
    ]

    breadth = make_breadth(
        MarketDirection.BEARISH,
    )

    result = scanner.scan(
        indices,
        breadth,
    )

    assert result.regime == MarketRegime.STRONG_BEARISH
    assert result.score == -6
    assert result.strongest_index == "NIFTY"
    assert result.weakest_index == "BANKNIFTY"
    assert result.status == MarketDataStatus.LIVE


def test_mixed_market_is_neutral():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
        ),
        make_index(
            "BANKNIFTY",
            -1.0,
            MarketDirection.BEARISH,
            -1,
        ),
    ]

    breadth = make_breadth(
        MarketDirection.NEUTRAL,
        score=0,
    )

    result = scanner.scan(
        indices,
        breadth,
    )

    assert result.regime == MarketRegime.NEUTRAL
    assert result.score == 0
    assert result.status == MarketDataStatus.LIVE


def test_bullish_without_breadth_is_not_strong():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
        ),
        make_index(
            "BANKNIFTY",
            1.5,
            MarketDirection.BULLISH,
            1,
        ),
    ]

    result = scanner.scan(indices)

    assert result.regime == MarketRegime.BULLISH
    assert result.score == 2
    assert result.breadth is None


def test_bearish_without_breadth_is_not_strong():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            -1.0,
            MarketDirection.BEARISH,
            -1,
        ),
        make_index(
            "BANKNIFTY",
            -1.5,
            MarketDirection.BEARISH,
            -1,
        ),
    ]

    result = scanner.scan(indices)

    assert result.regime == MarketRegime.BEARISH
    assert result.score == -2
    assert result.breadth is None


def test_strong_index_score_contributes_two_points():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            5,
        ),
    ]

    result = scanner.scan(indices)

    assert result.score == 2
    assert result.regime == MarketRegime.BULLISH


def test_stale_data_status():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
            MarketDataStatus.STALE,
        ),
    ]

    result = scanner.scan(indices)

    assert result.status == MarketDataStatus.STALE


def test_mock_data_status():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
            MarketDataStatus.MOCK,
        ),
    ]

    result = scanner.scan(indices)

    assert result.status == MarketDataStatus.MOCK


def test_live_data_has_priority_over_mock_and_stale():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
            MarketDataStatus.LIVE,
        ),
        make_index(
            "BANKNIFTY",
            0.5,
            MarketDirection.BULLISH,
            1,
            MarketDataStatus.MOCK,
        ),
        make_index(
            "FINNIFTY",
            -0.2,
            MarketDirection.BEARISH,
            -1,
            MarketDataStatus.STALE,
        ),
    ]

    result = scanner.scan(indices)

    assert result.status == MarketDataStatus.LIVE


def test_none_entries_are_ignored():
    scanner = MarketScanner()

    indices = [
        make_index(
            "NIFTY",
            1.0,
            MarketDirection.BULLISH,
            1,
        ),
        None,
    ]

    result = scanner.scan(indices)

    assert len(result.indices) == 1
    assert result.indices[0].symbol == "NIFTY"


def test_reasons_are_generated():
    scanner = MarketScanner()

    result = scanner.scan(
        [
            make_index(
                "NIFTY",
                1.0,
                MarketDirection.BULLISH,
                1,
            )
        ],
        make_breadth(MarketDirection.BULLISH),
    )

    assert len(result.reasons) >= 3
    assert any("Index contribution" in reason for reason in result.reasons)
    assert any("Breadth contribution" in reason for reason in result.reasons)