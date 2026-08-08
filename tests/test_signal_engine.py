from datetime import datetime

from batip.analytics.signal import Signal
from batip.analytics.signal_engine import SignalEngine
from batip.models.option_chain import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)


class MaxPain:
    def __init__(self, strike):
        self.strike = strike


class SupportResistance:
    def __init__(self, support, resistance):
        self.support = support
        self.resistance = resistance


def create_chain(
    spot=58145.25,
    call_oi=100,
    put_oi=150,
    call_change=10,
    put_change=20,
):
    chain = OptionChain(
        symbol="BANKNIFTY",
        expiry="13-Aug-2026",
        spot_price=spot,
        timestamp=datetime.now(),
    )

    call = OptionLeg(
        strike=58100,
        option_type="CE",
        last_price=100,
        bid_price=99,
        ask_price=101,
        volume=1000,
        open_interest=call_oi,
        change_in_oi=call_change,
        implied_volatility=15,
    )

    put = OptionLeg(
        strike=58100,
        option_type="PE",
        last_price=100,
        bid_price=99,
        ask_price=101,
        volume=1000,
        open_interest=put_oi,
        change_in_oi=put_change,
        implied_volatility=15,
    )

    chain.strikes.append(
        OptionStrike(
            strike=58100,
            call=call,
            put=put,
        )
    )

    return chain


def test_strong_buy_signal():
    chain = create_chain(
        spot=58200,
        call_oi=100,
        put_oi=200,
        call_change=10,
        put_change=30,
    )

    result = SignalEngine(
        chain=chain,
        pcr=1.25,
        max_pain=MaxPain(58100),
        support_resistance=SupportResistance(
            support=58000,
            resistance=58150,
        ),
    ).calculate()

    assert result.signal == Signal.STRONG_BUY
    assert result.score >= 7
    assert result.direction == "Bullish"
    assert result.confidence > 50


def test_strong_sell_signal():
    chain = create_chain(
        spot=58000,
        call_oi=200,
        put_oi=100,
        call_change=30,
        put_change=10,
    )

    result = SignalEngine(
        chain=chain,
        pcr=0.70,
        max_pain=MaxPain(58100),
        support_resistance=SupportResistance(
            support=58050,
            resistance=58200,
        ),
    ).calculate()

    assert result.signal == Signal.STRONG_SELL
    assert result.score <= -7
    assert result.direction == "Bearish"
    assert result.confidence > 50


def test_wait_signal():
    chain = create_chain(
        spot=58100,
        call_oi=100,
        put_oi=100,
        call_change=10,
        put_change=10,
    )

    result = SignalEngine(
        chain=chain,
        pcr=0.90,
        max_pain=MaxPain(58100),
        support_resistance=SupportResistance(
            support=58000,
            resistance=58200,
        ),
    ).calculate()

    assert result.signal == Signal.WAIT
    assert result.direction == "Neutral"