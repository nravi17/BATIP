from batip.market.stock import (
    StockVolumeEngine,
    StockVolumeSnapshot,
)


def make_volume(
    symbol: str,
    volume_change_percent: float,
    average_volume_ratio: float = 1.0,
) -> StockVolumeSnapshot:
    return StockVolumeSnapshot(
        symbol=symbol,
        volume_change_percent=volume_change_percent,
        average_volume_ratio=average_volume_ratio,
    )


def test_strong_positive_volume_score():
    engine = StockVolumeEngine()

    assert engine.score_volume(60) == 2


def test_positive_volume_score():
    engine = StockVolumeEngine()

    assert engine.score_volume(20) == 1


def test_neutral_volume_score():
    engine = StockVolumeEngine()

    assert engine.score_volume(0) == 0


def test_negative_volume_score():
    engine = StockVolumeEngine()

    assert engine.score_volume(-20) == -1


def test_strong_negative_volume_score():
    engine = StockVolumeEngine()

    assert engine.score_volume(-60) == -2


def test_volume_direction():
    engine = StockVolumeEngine()

    assert engine.direction_from_score(2) == "Bullish"
    assert engine.direction_from_score(1) == "Bullish"
    assert engine.direction_from_score(0) == "Neutral"
    assert engine.direction_from_score(-1) == "Bearish"
    assert engine.direction_from_score(-2) == "Bearish"


def test_high_volume_confirmation():
    engine = StockVolumeEngine()

    result = engine.analyze(
        make_volume(
            "TCS",
            volume_change_percent=60,
            average_volume_ratio=2.0,
        )
    )

    assert result.score == 2
    assert result.direction == "Bullish"
    assert result.volume_confirmation == "Strong"


def test_moderate_volume_confirmation():
    engine = StockVolumeEngine()

    result = engine.analyze(
        make_volume(
            "TCS",
            volume_change_percent=20,
            average_volume_ratio=1.2,
        )
    )

    assert result.score == 1
    assert result.direction == "Bullish"
    assert result.volume_confirmation == "Moderate"


def test_low_volume_confirmation():
    engine = StockVolumeEngine()

    result = engine.analyze(
        make_volume(
            "TCS",
            volume_change_percent=0,
            average_volume_ratio=1.0,
        )
    )

    assert result.score == 0
    assert result.direction == "Neutral"
    assert result.volume_confirmation == "Normal"


def test_volume_analysis():
    engine = StockVolumeEngine()

    result = engine.analyze(
        make_volume(
            "RELIANCE",
            volume_change_percent=60,
            average_volume_ratio=2.5,
        )
    )

    assert result.symbol == "RELIANCE"
    assert result.volume_change_percent == 60
    assert result.average_volume_ratio == 2.5
    assert result.score == 2
    assert result.direction == "Bullish"
    assert result.volume_confirmation == "Strong"


def test_negative_volume_analysis():
    engine = StockVolumeEngine()

    result = engine.analyze(
        make_volume(
            "INFY",
            volume_change_percent=-60,
            average_volume_ratio=0.5,
        )
    )

    assert result.score == -2
    assert result.direction == "Bearish"
    assert result.volume_confirmation == "Weak"