from batip.trading.models import TradeSetup


def test_trade_setup_defaults():
    setup = TradeSetup(
        symbol="TEST",
        direction="Bullish",
        entry=100.0,
        stop_loss=95.0,
        target_1=110.0,
        target_2=120.0,
    )

    assert setup.symbol == "TEST"
    assert setup.direction == "Bullish"
    assert setup.entry == 100.0
    assert setup.stop_loss == 95.0
    assert setup.target_1 == 110.0
    assert setup.target_2 == 120.0
    assert setup.position_size == 0
    assert setup.valid is True


def test_trade_setup_full_data():
    setup = TradeSetup(
        symbol="NIFTY",
        direction="Bullish",
        entry=24500.0,
        stop_loss=24400.0,
        target_1=24700.0,
        target_2=24900.0,
        risk_per_share=100.0,
        reward_1_per_share=200.0,
        reward_2_per_share=400.0,
        risk_reward_1=2.0,
        risk_reward_2=4.0,
        capital=100000.0,
        risk_percent=1.0,
        risk_amount=1000.0,
        position_size=10,
        maximum_loss=1000.0,
        intraday="FAVORABLE",
        overnight="FAVORABLE",
        confidence=90.0,
        invalidation="Below 24400",
    )

    assert setup.risk_amount == 1000.0
    assert setup.position_size == 10
    assert setup.risk_reward_1 == 2.0
    assert setup.risk_reward_2 == 4.0
    assert setup.confidence == 90.0