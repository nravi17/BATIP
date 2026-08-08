from batip.market.models import (
    IndexSnapshot,
    MarketBreadth,
    MarketDataStatus,
    MarketDirection,
    MarketRegime,
    MarketSnapshot,
)


def test_index_snapshot_defaults():
    snapshot = IndexSnapshot(
        symbol="NIFTY",
        name="NIFTY 50",
        value=25000.0,
    )

    assert snapshot.symbol == "NIFTY"
    assert snapshot.value == 25000.0
    assert snapshot.change == 0.0
    assert snapshot.change_percent == 0.0
    assert snapshot.direction == MarketDirection.NEUTRAL
    assert snapshot.status == MarketDataStatus.UNAVAILABLE


def test_index_snapshot_live_data():
    snapshot = IndexSnapshot(
        symbol="BANKNIFTY",
        name="NIFTY BANK",
        value=57746.45,
        change=250.50,
        change_percent=0.44,
        direction=MarketDirection.BULLISH,
        score=2,
        status=MarketDataStatus.LIVE,
    )

    assert snapshot.value == 57746.45
    assert snapshot.change_percent == 0.44
    assert snapshot.direction == MarketDirection.BULLISH
    assert snapshot.score == 2
    assert snapshot.status == MarketDataStatus.LIVE


def test_market_breadth():
    breadth = MarketBreadth(
        advances=1200,
        declines=600,
        unchanged=100,
        advance_decline_ratio=2.0,
        breadth_score=66.67,
        direction=MarketDirection.BULLISH,
        status=MarketDataStatus.LIVE,
    )

    assert breadth.advances == 1200
    assert breadth.declines == 600
    assert breadth.unchanged == 100
    assert breadth.advance_decline_ratio == 2.0
    assert breadth.direction == MarketDirection.BULLISH


def test_market_snapshot():
    nifty = IndexSnapshot(
        symbol="NIFTY",
        name="NIFTY 50",
        value=25000.0,
        change_percent=0.80,
        direction=MarketDirection.BULLISH,
        score=2,
        status=MarketDataStatus.LIVE,
    )

    banknifty = IndexSnapshot(
        symbol="BANKNIFTY",
        name="NIFTY BANK",
        value=57746.45,
        change_percent=1.10,
        direction=MarketDirection.BULLISH,
        score=2,
        status=MarketDataStatus.LIVE,
    )

    snapshot = MarketSnapshot(
        indices=[nifty, banknifty],
        regime=MarketRegime.BULLISH,
        score=4,
        strongest_index="BANKNIFTY",
        weakest_index="NIFTY",
        status=MarketDataStatus.LIVE,
    )

    assert len(snapshot.indices) == 2
    assert snapshot.regime == MarketRegime.BULLISH
    assert snapshot.score == 4
    assert snapshot.strongest_index == "BANKNIFTY"
    assert snapshot.weakest_index == "NIFTY"