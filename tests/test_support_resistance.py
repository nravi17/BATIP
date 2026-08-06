from batip.analytics.support_resistance import (
    SupportResistanceCalculator,
)


def test_support_resistance(option_chain):

    result = SupportResistanceCalculator(option_chain).calculate()

    assert result.support > 0

    assert result.resistance > 0

    assert result.support_oi > 0

    assert result.resistance_oi > 0