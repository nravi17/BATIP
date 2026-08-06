from batip.analytics.oi_analysis import OIAnalyzer


def test_oi(option_chain):

    result = OIAnalyzer(option_chain).analyze()

    assert len(result) > 0