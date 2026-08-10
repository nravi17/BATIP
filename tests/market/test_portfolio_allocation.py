from batip.market.portfolio import (
    PortfolioAllocationEngine,
    PortfolioAllocationSnapshot,
)


def make_input(
    symbol="TCS",
    action="BUY",
    available_capital=100000.0,
    entry_price=4000.0,
    stop_loss=3900.0,
    risk_percent=1.0,
    max_allocation_percent=50.0,
    confidence=90.0,
):
    return {
        "symbol": symbol,
        "action": action,
        "available_capital": available_capital,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "risk_percent": risk_percent,
        "max_allocation_percent": max_allocation_percent,
        "confidence": confidence,
    }


def test_allocation_engine_import():
    engine = PortfolioAllocationEngine()

    assert engine is not None


def test_buy_allocation():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert isinstance(
        result,
        PortfolioAllocationSnapshot,
    )

    assert result.symbol == "TCS"
    assert result.action == "BUY"


def test_risk_budget():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.risk_budget == 1000.0


def test_risk_per_share():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.risk_per_share == 100.0


def test_risk_based_position_size():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    # Risk budget = 1,000
    # Risk/share = 100
    # Position = 10
    assert result.position_size == 10


def test_capital_required():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.capital_required == 40000.0


def test_allocation_percent():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.allocation_percent == 40.0


def test_exposure_percent():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.exposure_percent == 40.0


def test_valid_allocation():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.allocation_status == "VALID"


def test_max_allocation_limits_position():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            max_allocation_percent=20.0
        )
    )

    # Maximum capital = 20,000
    # At 4,000/share => maximum 5 shares.
    assert result.position_size == 5
    assert result.capital_required == 20000.0
    assert result.allocation_percent == 20.0


def test_hold_is_not_actionable():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            action="HOLD"
        )
    )

    assert result.allocation_status == "NOT_ACTIONABLE"


def test_invalid_capital():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            available_capital=0
        )
    )

    assert result.allocation_status == "INVALID"
    assert result.position_size == 0


def test_invalid_entry():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            entry_price=0
        )
    )

    assert result.allocation_status == "INVALID"


def test_invalid_stop():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            stop_loss=4000
        )
    )

    assert result.allocation_status == "INVALID"


def test_confidence_preserved():
    engine = PortfolioAllocationEngine()

    result = engine.analyze(
        make_input(
            confidence=95.0
        )
    )

    assert result.confidence == 95.0


def test_none_input():
    engine = PortfolioAllocationEngine()

    assert engine.analyze(None) is None