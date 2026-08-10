from batip.market.portfolio import (
    PortfolioExecutionEngine,
    PortfolioExecutionSnapshot,
)


def make_input(
    symbol="TCS",
    action="BUY",
    entry_price=4000.0,
    stop_loss=3900.0,
    target_1=4300.0,
    target_2=4500.0,
    capital=100000.0,
    risk_percent=1.0,
    confidence=90.0,
):
    return {
        "symbol": symbol,
        "action": action,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_1": target_1,
        "target_2": target_2,
        "capital": capital,
        "risk_percent": risk_percent,
        "confidence": confidence,
    }


def test_execution_engine_import():
    engine = PortfolioExecutionEngine()

    assert engine is not None


def test_buy_execution():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    assert isinstance(
        result,
        PortfolioExecutionSnapshot,
    )

    assert result.symbol == "TCS"
    assert result.action == "BUY"
    assert result.entry_price == 4000.0
    assert result.stop_loss == 3900.0
    assert result.target_1 == 4300.0
    assert result.target_2 == 4500.0


def test_risk_per_share():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.risk_per_share == 100.0


def test_position_size():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    # Capital = 100,000
    # Risk = 1% = 1,000
    # Risk/share = 100
    # Position = 10
    assert result.position_size == 10


def test_capital_required():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.capital_required == 40000.0


def test_max_loss():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.max_loss == 1000.0


def test_risk_reward():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    # Reward = 4300 - 4000 = 300
    # Risk = 4000 - 3900 = 100
    assert result.risk_reward == 3.0


def test_valid_execution():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input()
    )

    assert result.execution_status == "VALID"


def test_non_buy_is_not_actionable():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(action="HOLD")
    )

    assert result.execution_status == "NOT_ACTIONABLE"


def test_invalid_stop_loss():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(
            stop_loss=4100.0
        )
    )

    assert result.execution_status == "INVALID"


def test_invalid_target():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(
            target_1=3900.0
        )
    )

    assert result.execution_status == "INVALID"


def test_weak_risk_reward():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(
            target_1=4100.0
        )
    )

    assert result.execution_status == "WEAK_RISK_REWARD"


def test_zero_entry_price():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(
            entry_price=0
        )
    )

    assert result.execution_status == "INVALID"
    assert result.position_size == 0
    assert result.max_loss == 0.0


def test_none_input():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(None)

    assert result is None


def test_confidence_is_preserved():
    engine = PortfolioExecutionEngine()

    result = engine.analyze(
        make_input(
            confidence=95.0
        )
    )

    assert result.confidence == 95.0