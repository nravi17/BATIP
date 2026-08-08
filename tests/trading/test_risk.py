from batip.trading.risk import RiskEngine


def test_risk_amount():
    assert RiskEngine.risk_amount(
        100000,
        1,
    ) == 1000


def test_risk_per_share():
    assert RiskEngine.risk_per_share(
        1520,
        1500,
    ) == 20


def test_long_position_size():
    assert RiskEngine.position_size(
        100000,
        1,
        1520,
        1500,
    ) == 50


def test_short_position_size():
    assert RiskEngine.position_size(
        100000,
        1,
        1520,
        1540,
    ) == 50


def test_maximum_loss():
    assert RiskEngine.maximum_loss(
        50,
        1520,
        1500,
    ) == 1000


def test_risk_reward():
    assert RiskEngine.risk_reward(
        1520,
        1500,
        1550,
    ) == 1.5


def test_valid_long_direction():
    valid, reason = RiskEngine.validate_direction(
        "Bullish",
        1520,
        1500,
        1550,
        1580,
    )

    assert valid is True
    assert "valid" in reason.lower()


def test_valid_short_direction():
    valid, reason = RiskEngine.validate_direction(
        "Bearish",
        1520,
        1540,
        1490,
        1460,
    )

    assert valid is True
    assert "valid" in reason.lower()


def test_invalid_long_stop():
    valid, reason = RiskEngine.validate_direction(
        "Bullish",
        1520,
        1530,
        1550,
        1580,
    )

    assert valid is False
    assert "stop loss" in reason.lower()


def test_invalid_short_stop():
    valid, reason = RiskEngine.validate_direction(
        "Bearish",
        1520,
        1510,
        1490,
        1460,
    )

    assert valid is False
    assert "stop loss" in reason.lower()


def test_invalid_long_targets():
    valid, reason = RiskEngine.validate_direction(
        "Bullish",
        1520,
        1500,
        1510,
        1580,
    )

    assert valid is False
    assert "target 1" in reason.lower()


def test_invalid_short_targets():
    valid, reason = RiskEngine.validate_direction(
        "Bearish",
        1520,
        1540,
        1530,
        1460,
    )

    assert valid is False
    assert "target 1" in reason.lower()


def test_invalid_direction():
    valid, reason = RiskEngine.validate_direction(
        "Unknown",
        1520,
        1500,
        1550,
        1580,
    )

    assert valid is False


def test_good_risk_reward():
    valid, reason = RiskEngine.validate_risk_reward(
        1520,
        1500,
        1550,
        1.5,
    )

    assert valid is True


def test_bad_risk_reward():
    valid, reason = RiskEngine.validate_risk_reward(
        1520,
        1500,
        1530,
        1.5,
    )

    assert valid is False


def test_zero_risk_returns_zero_position():
    assert RiskEngine.position_size(
        100000,
        1,
        1520,
        1520,
    ) == 0


def test_invalid_capital_returns_zero():
    assert RiskEngine.position_size(
        0,
        1,
        1520,
        1500,
    ) == 0