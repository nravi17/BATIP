from batip.market.stock import (
    StockSnapshot,
    StockStrengthEngine,
)


def make_stock(
    symbol: str,
    change_percent: float,
    sector: str,
    score: int = 0,
) -> StockSnapshot:
    return StockSnapshot(
        symbol=symbol,
        name=symbol,
        sector=sector,
        change_percent=change_percent,
        score=score,
    )


def test_strong_bullish_stock_score():
    engine = StockStrengthEngine()

    assert engine.score_stock(2.0) == 2


def test_bullish_stock_score():
    engine = StockStrengthEngine()

    assert engine.score_stock(0.50) == 1


def test_neutral_stock_score():
    engine = StockStrengthEngine()

    assert engine.score_stock(0.0) == 0


def test_bearish_stock_score():
    engine = StockStrengthEngine()

    assert engine.score_stock(-0.50) == -1


def test_strong_bearish_stock_score():
    engine = StockStrengthEngine()

    assert engine.score_stock(-2.0) == -2


def test_stock_strength_ranking():
    engine = StockStrengthEngine()

    stocks = [
        make_stock("TCS", 1.80, "IT"),
        make_stock("HDFCBANK", 0.90, "BANK"),
        make_stock("MARUTI", -0.20, "AUTO"),
        make_stock("SUNPHARMA", -1.50, "PHARMA"),
    ]

    result = engine.analyze(stocks)

    assert len(result) == 4

    assert result[0].symbol == "TCS"
    assert result[1].symbol == "HDFCBANK"
    assert result[2].symbol == "MARUTI"
    assert result[3].symbol == "SUNPHARMA"

    assert result[0].score == 2
    assert result[-1].score == -2


def test_strongest_stock():
    engine = StockStrengthEngine()

    stocks = [
        make_stock("TCS", 1.80, "IT"),
        make_stock("HDFCBANK", 0.90, "BANK"),
        make_stock("MARUTI", -0.20, "AUTO"),
    ]

    result = engine.analyze(stocks)

    strongest = engine.strongest(result)

    assert strongest is not None
    assert strongest.symbol == "TCS"


def test_weakest_stock():
    engine = StockStrengthEngine()

    stocks = [
        make_stock("TCS", 1.80, "IT"),
        make_stock("HDFCBANK", 0.90, "BANK"),
        make_stock("MARUTI", -0.20, "AUTO"),
    ]

    result = engine.analyze(stocks)

    weakest = engine.weakest(result)

    assert weakest is not None
    assert weakest.symbol == "MARUTI"


def test_empty_stock_list():
    engine = StockStrengthEngine()

    result = engine.analyze([])

    assert result == []
    assert engine.strongest(result) is None
    assert engine.weakest(result) is None


def test_none_stocks_are_ignored():
    engine = StockStrengthEngine()

    stocks = [
        make_stock("TCS", 1.50, "IT"),
        None,
        make_stock("INFY", 0.80, "IT"),
    ]

    result = engine.analyze(stocks)

    assert len(result) == 2
    assert result[0].symbol == "TCS"
    assert result[1].symbol == "INFY"


def test_original_stock_objects_are_not_mutated():
    engine = StockStrengthEngine()

    stock = make_stock("TCS", 1.50, "IT")

    engine.analyze([stock])

    assert stock.score == 0