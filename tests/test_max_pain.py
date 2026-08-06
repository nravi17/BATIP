from batip.analytics.max_pain import MaxPainCalculator


def test_max_pain(option_chain):

    result = MaxPainCalculator(option_chain).calculate()

    assert result.strike > 0

    assert result.total_pain >= 0