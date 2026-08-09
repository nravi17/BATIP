from dataclasses import dataclass

import pytest

from batip.market.service import MarketService, MarketSummary


@dataclass
class Symbol:
    symbol: str
    change_percent: float


def test_market_service_creation():
    service = MarketService()

    assert service.symbols == []


def test_load_symbols():
    service = MarketService()

    symbols = [
        Symbol("RELIANCE", 2.5),
        Symbol("HDFCBANK", -1.2),
        Symbol("INFY", 0.0),
    ]

    count = service.load_symbols(symbols)

    assert count == 3
    assert len(service.symbols) == 3


def test_add_symbol():
    service = MarketService()

    service.add_symbol(
        Symbol("RELIANCE", 2.5)
    )

    assert len(service.symbols) == 1
    assert service.symbols[0].symbol == "RELIANCE"


def test_add_none_symbol_is_rejected():
    service = MarketService()

    with pytest.raises(ValueError):
        service.add_symbol(None)


def test_clear_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.5),
            Symbol("INFY", 1.0),
        ]
    )

    service.clear()

    assert service.symbols == []


def test_symbol_name_is_normalized():
    service = MarketService()

    record = Symbol(" reliance ", 2.0)

    assert service.symbol_name(record) == "RELIANCE"


def test_dictionary_symbol_is_supported():
    service = MarketService()

    record = {
        "symbol": "TCS",
        "change_percent": 1.5,
    }

    assert service.symbol_name(record) == "TCS"
    assert service.price_change(record) == 1.5


def test_price_change():
    service = MarketService()

    record = Symbol("RELIANCE", 2.75)

    assert service.price_change(record) == 2.75


def test_invalid_price_change_returns_zero():
    service = MarketService()

    record = {
        "symbol": "RELIANCE",
        "change_percent": "invalid",
    }

    assert service.price_change(record) == 0.0


def test_bullish_classification():
    service = MarketService()

    assert (
        service.classify_symbol(
            Symbol("RELIANCE", 2.0)
        )
        == "BULLISH"
    )


def test_bearish_classification():
    service = MarketService()

    assert (
        service.classify_symbol(
            Symbol("RELIANCE", -2.0)
        )
        == "BEARISH"
    )


def test_neutral_classification():
    service = MarketService()

    assert (
        service.classify_symbol(
            Symbol("RELIANCE", 0.0)
        )
        == "NEUTRAL"
    )


def test_bullish_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
            Symbol("HDFCBANK", -1.0),
            Symbol("INFY", 0.0),
            Symbol("TCS", 3.0),
        ]
    )

    bullish = service.bullish_symbols()

    assert len(bullish) == 2
    assert service.symbol_name(bullish[0]) in {
        "RELIANCE",
        "TCS",
    }


def test_bearish_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
            Symbol("HDFCBANK", -1.0),
            Symbol("INFY", -2.0),
        ]
    )

    bearish = service.bearish_symbols()

    assert len(bearish) == 2


def test_neutral_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
            Symbol("HDFCBANK", 0.0),
            Symbol("INFY", 0.0),
        ]
    )

    neutral = service.neutral_symbols()

    assert len(neutral) == 2


def test_average_change():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", 2.0),
            Symbol("B", 4.0),
            Symbol("C", -1.0),
        ]
    )

    assert service.average_change() == pytest.approx(5 / 3)


def test_empty_average_change():
    service = MarketService()

    assert service.average_change() == 0.0


def test_bullish_breadth():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", 2.0),
            Symbol("B", 1.0),
            Symbol("C", -1.0),
        ]
    )

    assert service.breadth() == "BULLISH"


def test_bearish_breadth():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", -2.0),
            Symbol("B", -1.0),
            Symbol("C", 1.0),
        ]
    )

    assert service.breadth() == "BEARISH"


def test_neutral_breadth():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", 2.0),
            Symbol("B", -2.0),
        ]
    )

    assert service.breadth() == "NEUTRAL"


def test_summary():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
            Symbol("HDFCBANK", -1.0),
            Symbol("INFY", 0.0),
            Symbol("TCS", 3.0),
        ]
    )

    result = service.summary("NSE")

    assert isinstance(result, MarketSummary)
    assert result.market == "NSE"
    assert result.total_symbols == 4
    assert result.bullish_symbols == 2
    assert result.bearish_symbols == 1
    assert result.neutral_symbols == 1
    assert result.average_change == 1.0
    assert result.breadth == "BULLISH"


def test_get_symbol():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
            Symbol("INFY", -1.0),
        ]
    )

    result = service.get_symbol("reliance")

    assert result is not None
    assert result.symbol == "RELIANCE"


def test_get_missing_symbol():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("RELIANCE", 2.0),
        ]
    )

    assert service.get_symbol("TCS") is None


def test_analyze_with_symbols():
    service = MarketService()

    result = service.analyze(
        [
            Symbol("A", 2.0),
            Symbol("B", -1.0),
        ],
        market="BSE",
    )

    assert result.market == "BSE"
    assert result.total_symbols == 2
    assert result.bullish_symbols == 1
    assert result.bearish_symbols == 1
    assert result.breadth == "NEUTRAL"


def test_analyze_existing_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", 1.0),
            Symbol("B", 2.0),
        ]
    )

    result = service.analyze()

    assert result.total_symbols == 2
    assert result.breadth == "BULLISH"


def test_load_none_clears_symbols():
    service = MarketService()

    service.load_symbols(
        [
            Symbol("A", 1.0),
        ]
    )

    assert service.load_symbols(None) == 0
    assert service.symbols == []