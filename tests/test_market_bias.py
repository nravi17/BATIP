from datetime import datetime

from batip.analytics.market_bias import (
    MarketBias,
    MarketBiasEngine,
)
from batip.models.option_chain import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)


def create_chain(
    call_oi=100,
    put_oi=150,
    call_change=10,
    put_change=20,
):
    chain = OptionChain(
        symbol="BANKNIFTY",
        expiry="13-Aug-2026",
        spot_price=58145.25,
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


def test_bullish_bias():
    chain = create_chain()

    result = MarketBiasEngine(
        chain,
        pcr=1.25,
    ).calculate()

    assert result.bias == MarketBias.STRONG_BULLISH
    assert result.score >= 3
    assert result.confidence > 50


def test_bearish_bias():
    chain = create_chain(
        call_oi=200,
        put_oi=100,
        call_change=30,
        put_change=10,
    )

    result = MarketBiasEngine(
        chain,
        pcr=0.70,
    ).calculate()

    assert result.bias == MarketBias.STRONG_BEARISH
    assert result.score <= -3


def test_neutral_bias():
    chain = create_chain(
        call_oi=100,
        put_oi=100,
        call_change=10,
        put_change=10,
    )

    result = MarketBiasEngine(
        chain,
        pcr=0.90,
    ).calculate()

    assert result.bias == MarketBias.NEUTRAL