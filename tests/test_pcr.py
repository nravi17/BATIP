from batip.analytics.pcr import PCRCalculator


def test_pcr(option_chain):

    result = PCRCalculator(option_chain).calculate()

    assert result.name == "PCR"

    assert result.value > 0

    assert result.signal in [
        "Bearish",
        "Neutral",
        "Bullish",
        "Extreme Bullish",
    ]