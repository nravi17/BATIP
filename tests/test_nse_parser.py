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