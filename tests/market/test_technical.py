from batip.market.technical import TechnicalScanner


def test_bullish_trend():
    scanner = TechnicalScanner()

    assert scanner.trend_score(
        price=110,
        short_ma=105,
        long_ma=100,
    ) == 2


def test_partial_bullish_trend():
    scanner = TechnicalScanner()

    assert scanner.trend_score(
        price=110,
        short_ma=105,
        long_ma=115,
    ) == 1


def test_bearish_trend():
    scanner = TechnicalScanner()

    assert scanner.trend_score(
        price=90,
        short_ma=95,
        long_ma=100,
    ) == -2


def test_partial_bearish_trend():
    scanner = TechnicalScanner()

    assert scanner.trend_score(
        price=90,
        short_ma=95,
        long_ma=85,
    ) == -1


def test_neutral_trend():
    scanner = TechnicalScanner()

    assert scanner.trend_score(
        price=100,
        short_ma=100,
        long_ma=100,
    ) == 0


def test_momentum_score():
    scanner = TechnicalScanner()

    assert scanner.momentum_score(2.5) == 2
    assert scanner.momentum_score(0.5) == 1
    assert scanner.momentum_score(0) == 0
    assert scanner.momentum_score(-0.5) == -1
    assert scanner.momentum_score(-2.5) == -2


def test_breakout_score():
    scanner = TechnicalScanner()

    assert scanner.breakout_score(
        price=110,
        resistance=105,
        support=95,
    ) == 2

    assert scanner.breakout_score(
        price=90,
        resistance=105,
        support=95,
    ) == -2

    assert scanner.breakout_score(
        price=100,
        resistance=105,
        support=95,
    ) == 0


def test_relative_strength():
    scanner = TechnicalScanner()

    assert scanner.relative_strength_score(
        stock_change_percent=3.0,
        benchmark_change_percent=0.5,
    ) == 2

    assert scanner.relative_strength_score(
        stock_change_percent=1.0,
        benchmark_change_percent=0.5,
    ) == 1

    assert scanner.relative_strength_score(
        stock_change_percent=0.5,
        benchmark_change_percent=0.5,
    ) == 0

    assert scanner.relative_strength_score(
        stock_change_percent=-1.0,
        benchmark_change_percent=0.0,
    ) == -1

    assert scanner.relative_strength_score(
        stock_change_percent=-3.0,
        benchmark_change_percent=0.0,
    ) == -2


def test_volume_confirmation():
    scanner = TechnicalScanner()

    assert scanner.volume_confirmation_score(
        price_change_percent=2.0,
        volume_change_percent=60,
    ) == 2

    assert scanner.volume_confirmation_score(
        price_change_percent=1.0,
        volume_change_percent=20,
    ) == 1

    assert scanner.volume_confirmation_score(
        price_change_percent=-2.0,
        volume_change_percent=60,
    ) == -2

    assert scanner.volume_confirmation_score(
        price_change_percent=-1.0,
        volume_change_percent=20,
    ) == -1

    assert scanner.volume_confirmation_score(
        price_change_percent=1.0,
        volume_change_percent=-10,
    ) == 0


def test_direction_mapping():
    scanner = TechnicalScanner()

    assert scanner.direction_from_score(5) == "Bullish"
    assert scanner.direction_from_score(0) == "Neutral"
    assert scanner.direction_from_score(-5) == "Bearish"


def test_confidence_mapping():
    scanner = TechnicalScanner()

    assert scanner.confidence_from_score(0) == 50.0
    assert scanner.confidence_from_score(5) == 75.0
    assert scanner.confidence_from_score(10) == 95.0
    assert scanner.confidence_from_score(-10) == 95.0


def test_complete_bullish_analysis():
    scanner = TechnicalScanner()

    result = scanner.analyze(
        price=110,
        short_ma=105,
        long_ma=100,
        momentum=2.5,
        resistance=105,
        support=95,
        stock_change_percent=3.0,
        benchmark_change_percent=0.5,
        volume_change_percent=60,
    )

    assert result.trend_score == 2
    assert result.momentum_score == 2
    assert result.breakout_score == 2
    assert result.relative_strength_score == 2
    assert result.volume_score == 2

    assert result.score == 10
    assert result.direction == "Bullish"
    assert result.confidence == 95.0


def test_complete_bearish_analysis():
    scanner = TechnicalScanner()

    result = scanner.analyze(
        price=90,
        short_ma=95,
        long_ma=100,
        momentum=-2.5,
        resistance=105,
        support=95,
        stock_change_percent=-3.0,
        benchmark_change_percent=0.5,
        volume_change_percent=60,
    )

    assert result.score == -10
    assert result.direction == "Bearish"
    assert result.confidence == 95.0