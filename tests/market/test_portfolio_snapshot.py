from batip.market.portfolio import (
    PortfolioSnapshot,
    PortfolioSnapshotEngine,
)


def make_holding(
    symbol: str,
    quantity: int,
    average_price: float,
    current_price: float,
    sector: str = "IT",
):
    return {
        "symbol": symbol,
        "quantity": quantity,
        "average_price": average_price,
        "current_price": current_price,
        "sector": sector,
    }


def test_portfolio_snapshot_imports():
    engine = PortfolioSnapshotEngine()

    assert engine is not None


def test_single_holding_value():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding(
                "TCS",
                quantity=10,
                average_price=3000,
                current_price=3300,
            )
        ]
    )

    assert isinstance(result, PortfolioSnapshot)
    assert result.total_invested == 30000
    assert result.total_value == 33000
    assert result.total_pnl == 3000
    assert result.total_pnl_percent == 10.0


def test_multiple_holdings():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding(
                "TCS",
                10,
                3000,
                3300,
                "IT",
            ),
            make_holding(
                "HDFCBANK",
                20,
                1500,
                1600,
                "BANK",
            ),
        ]
    )

    assert result.total_invested == 60000
    assert result.total_value == 65000
    assert result.total_pnl == 5000


def test_portfolio_pnl_percent():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding(
                "TCS",
                10,
                3000,
                3300,
            ),
            make_holding(
                "INFY",
                10,
                1500,
                1350,
            ),
        ]
    )

    assert result.total_invested == 45000
    assert result.total_value == 46500
    assert result.total_pnl == 1500
    assert result.total_pnl_percent == 3.3333333333333335


def test_empty_portfolio():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze([])

    assert isinstance(result, PortfolioSnapshot)
    assert result.total_invested == 0
    assert result.total_value == 0
    assert result.total_pnl == 0
    assert result.total_pnl_percent == 0
    assert result.holding_count == 0


def test_none_holdings_are_ignored():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding("TCS", 10, 3000, 3300),
            None,
            make_holding("INFY", 10, 1500, 1350),
        ]
    )

    assert result.holding_count == 2
    assert result.total_invested == 45000
    assert result.total_value == 46500


def test_holding_count():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding("TCS", 10, 3000, 3300),
            make_holding("INFY", 10, 1500, 1350),
            make_holding("HDFCBANK", 20, 1500, 1600),
        ]
    )

    assert result.holding_count == 3


def test_sector_exposure():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding("TCS", 10, 3000, 3300, "IT"),
            make_holding("INFY", 10, 1500, 1350, "IT"),
            make_holding("HDFCBANK", 20, 1500, 1600, "BANK"),
        ]
    )

    assert result.sector_exposure["IT"] == 46500
    assert result.sector_exposure["BANK"] == 32000


def test_original_holdings_are_not_mutated():
    engine = PortfolioSnapshotEngine()

    holding = make_holding(
        "TCS",
        10,
        3000,
        3300,
    )

    engine.analyze([holding])

    assert holding["quantity"] == 10
    assert holding["average_price"] == 3000
    assert holding["current_price"] == 3300


def test_negative_pnl():
    engine = PortfolioSnapshotEngine()

    result = engine.analyze(
        [
            make_holding(
                "TCS",
                10,
                3000,
                2700,
            )
        ]
    )

    assert result.total_invested == 30000
    assert result.total_value == 27000
    assert result.total_pnl == -3000
    assert result.total_pnl_percent == -10.0