from batip.market.stock import (
    StockScanner,
    StockSnapshot,
)


def test_strong_positive_price_score():
    assert StockScanner.price_score(2.5) == 2


def test_positive_price_score():
    assert StockScanner.price_score(0.8) == 1


def test_negative_price_score():
    assert StockScanner.price_score(-0.8) == -1


def test_strong_negative_price_score():
    assert StockScanner.price_score(-2.5) == -2


def test_momentum_score():
    assert StockScanner.momentum_score(2.5) == 2
    assert StockScanner.momentum_score(0.5) == 1
    assert StockScanner.momentum_score(0.0) == 0
    assert StockScanner.momentum_score(-0.5) == -1
    assert StockScanner.momentum_score(-2.5) == -2


def test_volume_score():
    assert StockScanner.volume_score(60) == 2
    assert StockScanner.volume_score(20) == 1
    assert StockScanner.volume_score(0) == 0
    assert StockScanner.volume_score(-20) == -1
    assert StockScanner.volume_score(-60) == -2


def test_recommendation_mapping():
    assert StockScanner.recommendation_from_score(8) == "STRONG BUY"
    assert StockScanner.recommendation_from_score(5) == "BUY"
    assert StockScanner.recommendation_from_score(0) == "WATCH"
    assert StockScanner.recommendation_from_score(-5) == "SELL"
    assert StockScanner.recommendation_from_score(-8) == "STRONG SELL"


def test_direction_mapping():
    assert StockScanner.direction_from_score(5) == "Bullish"
    assert StockScanner.direction_from_score(0) == "Neutral"
    assert StockScanner.direction_from_score(-5) == "Bearish"


def test_stock_analysis():
    scanner = StockScanner()

    stock = StockSnapshot(
        symbol="TEST",
        name="Test Stock",
        price=1000,
        change_percent=2.5,
        momentum=2.5,
        volume=1000000,
        volume_change_percent=60,
        sector_score=2,
        liquidity_score=2,
    )

    result = scanner.analyze(stock)

    assert result.score == 10
    assert result.direction == "Bullish"
    assert result.recommendation == "STRONG BUY"


def test_negative_stock_analysis():
    scanner = StockScanner()

    stock = StockSnapshot(
        symbol="TEST",
        change_percent=-2.5,
        momentum=-2.5,
        volume_change_percent=-60,
        sector_score=-2,
        liquidity_score=-2,
    )

    result = scanner.analyze(stock)

    assert result.score == -10
    assert result.direction == "Bearish"
    assert result.recommendation == "STRONG SELL"


def test_stock_ranking():
    scanner = StockScanner()

    stocks = [
        StockSnapshot(
            symbol="A",
            change_percent=2.5,
            momentum=2.5,
            volume_change_percent=60,
            sector_score=2,
            liquidity_score=2,
        ),
        StockSnapshot(
            symbol="B",
            change_percent=0.5,
            momentum=0.5,
            volume_change_percent=10,
            sector_score=1,
            liquidity_score=1,
        ),
        StockSnapshot(
            symbol="C",
            change_percent=-2.5,
            momentum=-2.5,
            volume_change_percent=-60,
            sector_score=-2,
            liquidity_score=-2,
        ),
    ]

    result = scanner.rank(stocks)

    assert [stock.symbol for stock in result] == [
        "A",
        "B",
        "C",
    ]