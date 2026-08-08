from datetime import datetime

from batip.analytics.support_resistance import (
    SupportResistanceCalculator,
)
from batip.models.option_chain import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)


def create_chain():
    chain = OptionChain(
        symbol="BANKNIFTY",
        expiry="13-Aug-2026",
        spot_price=58145.25,
        timestamp=datetime.now(),
    )

    test_data = [
        (58000, 500000, 300000),
        (58100, 600000, 400000),
        (58200, 300000, 700000),
        (58300, 200000, 800000),
        (59100, 900000, 1000000),
        (57100, 1000000, 100000),
    ]

    for strike, put_oi, call_oi in test_data:

        call = OptionLeg(
            strike=strike,
            option_type="CE",
            last_price=100,
            bid_price=99,
            ask_price=101,
            volume=1000,
            open_interest=call_oi,
            change_in_oi=100,
            implied_volatility=15,
        )

        put = OptionLeg(
            strike=strike,
            option_type="PE",
            last_price=100,
            bid_price=99,
            ask_price=101,
            volume=1000,
            open_interest=put_oi,
            change_in_oi=100,
            implied_volatility=15,
        )

        chain.strikes.append(
            OptionStrike(
                strike=strike,
                call=call,
                put=put,
            )
        )

    return chain


def test_support_is_below_spot():
    chain = create_chain()

    result = SupportResistanceCalculator(chain).calculate()

    assert result.support < chain.spot_price


def test_resistance_is_above_spot():
    chain = create_chain()

    result = SupportResistanceCalculator(chain).calculate()

    assert result.resistance > chain.spot_price


def test_support_resistance_ignore_wrong_side_oi():
    chain = create_chain()

    result = SupportResistanceCalculator(chain).calculate()

    # 59,100 has very high Put OI but is above spot.
    # Therefore it must NOT become support.
    assert result.support != 59100

    # 57,100 has very high Call OI but is below spot.
    # Therefore it must NOT become resistance.
    assert result.resistance != 57100