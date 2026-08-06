from datetime import datetime

from batip.models import (
    OptionChain,
    OptionLeg,
    OptionStrike,
)


def create_sample_chain() -> OptionChain:
    """
    Creates a sample option chain for analytics testing.
    """

    chain = OptionChain(
        symbol="BANKNIFTY",
        expiry="13-Aug-2026",
        spot_price=58145.25,
        timestamp=datetime.now(),
    )

    sample = [
        (57800, 100000, 320000),
        (57900, 150000, 290000),
        (58000, 400000, 410000),
        (58100, 280000, 170000),
        (58200, 150000, 110000),
    ]

    for strike, call_oi, put_oi in sample:

        call = OptionLeg(
            strike=strike,
            option_type="CE",
            last_price=100,
            bid_price=99,
            ask_price=101,
            volume=1000,
            open_interest=call_oi,
            change_in_oi=0,
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
            change_in_oi=0,
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