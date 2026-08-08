from batip.providers.nse_parser import NSEParser

sample_payload = {
    "records": {
        "underlying": "BANKNIFTY",
        "underlyingValue": 58145.25,
        "expiryDates": ["13-Aug-2026"],
        "data": [
            {
                "strikePrice": 58000,
                "CE": {
                    "lastPrice": 120,
                    "bidprice": 119,
                    "askPrice": 121,
                    "openInterest": 400000,
                    "changeinOpenInterest": 12000,
                    "totalTradedVolume": 25000,
                    "impliedVolatility": 14.8,
                },
                "PE": {
                    "lastPrice": 98,
                    "bidprice": 97,
                    "askPrice": 99,
                    "openInterest": 420000,
                    "changeinOpenInterest": 18000,
                    "totalTradedVolume": 21000,
                    "impliedVolatility": 15.1,
                },
            }
        ],
    }
}


def test_parser():
    parser = NSEParser()
    chain = parser.parse_option_chain(sample_payload)
    assert chain.symbol == "BANKNIFTY"
    assert len(chain.strikes) == 1
    strike = chain.strikes[0]
    assert strike.call.open_interest == 400000
    assert strike.put.open_interest == 420000
    assert strike.call.last_price == 120
    assert strike.put.last_price == 98


def test_parser_maps_price_change_fields():
    payload = {
        "records": {
            "underlying": "BANKNIFTY",
            "underlyingValue": 58145.25,
            "expiryDates": ["13-Aug-2026"],
            "data": [
                {
                    "strikePrice": 58100,
                    "CE": {
                        "lastPrice": 250.0,
                        "bidprice": 249.0,
                        "askPrice": 251.0,
                        "totalTradedVolume": 10000,
                        "openInterest": 200000,
                        "changeinOpenInterest": 15000,
                        "impliedVolatility": 14.5,
                        "prevClose": 240.0,
                        "change": 10.0,
                        "pChange": 4.1667,
                    },
                    "PE": {
                        "lastPrice": 180.0,
                        "bidprice": 179.0,
                        "askPrice": 181.0,
                        "totalTradedVolume": 12000,
                        "openInterest": 300000,
                        "changeinOpenInterest": 25000,
                        "impliedVolatility": 15.2,
                        "prevClose": 175.0,
                        "change": 5.0,
                        "pChange": 2.8571,
                    },
                }
            ],
        }
    }

    chain = NSEParser().parse_option_chain(payload)

    leg = chain.strikes[0].call

    assert leg.last_price == 250.0
    assert leg.previous_close == 240.0
    assert leg.price_change == 10.0
    assert leg.price_change_percent == 4.1667
    assert leg.open_interest == 200000
    assert leg.change_in_oi == 15000