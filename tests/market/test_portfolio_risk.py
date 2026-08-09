from batip.market.portfolio import (
    PortfolioRiskEngine,
    PortfolioRiskSnapshot,
)


def make_holding(
    symbol: str,
    sector: str,
    weight: float,
    volatility: float,
    drawdown: float,
):
    return {
        "symbol": symbol,
        "sector": sector,
        "weight": weight,
        "volatility": volatility,
        "drawdown": drawdown,
    }


def test_portfolio_risk_imports():
    engine = PortfolioRiskEngine()

    assert engine is not None


def test_low_risk_portfolio():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 20.0, 15.0, -5.0),
        make_holding("HDFCBANK", "BANK", 20.0, 14.0, -4.0),
        make_holding("MARUTI", "AUTO", 20.0, 16.0, -6.0),
        make_holding("ITC", "FMCG", 20.0, 12.0, -3.0),
        make_holding("SUNPHARMA", "PHARMA", 20.0, 13.0, -4.0),
    ]

    result = engine.analyze(holdings)

    assert isinstance(result, PortfolioRiskSnapshot)
    assert result.risk_score < 30
    assert result.risk_classification == "LOW"


def test_moderate_risk_portfolio():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 30.0, 25.0, -12.0),
        make_holding("HDFCBANK", "BANK", 25.0, 22.0, -10.0),
        make_holding("MARUTI", "AUTO", 20.0, 24.0, -15.0),
        make_holding("ITC", "FMCG", 15.0, 18.0, -8.0),
        make_holding("SUNPHARMA", "PHARMA", 10.0, 20.0, -9.0),
    ]

    result = engine.analyze(holdings)

    assert result.risk_classification == "MODERATE"


def test_high_risk_portfolio():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 60.0, 40.0, -25.0),
        make_holding("INFY", "IT", 25.0, 38.0, -30.0),
        make_holding("WIPRO", "IT", 15.0, 42.0, -28.0),
    ]

    result = engine.analyze(holdings)

    assert result.risk_score >= 60
    assert result.risk_classification == "HIGH"


def test_concentration_risk_is_detected():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 70.0, 20.0, -8.0),
        make_holding("HDFCBANK", "BANK", 10.0, 18.0, -6.0),
        make_holding("MARUTI", "AUTO", 10.0, 20.0, -7.0),
        make_holding("ITC", "FMCG", 10.0, 15.0, -5.0),
    ]

    result = engine.analyze(holdings)

    assert result.concentration_risk is True


def test_sector_concentration_risk_is_detected():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 30.0, 20.0, -8.0),
        make_holding("INFY", "IT", 30.0, 22.0, -10.0),
        make_holding("WIPRO", "IT", 20.0, 24.0, -12.0),
        make_holding("HDFCBANK", "BANK", 20.0, 18.0, -6.0),
    ]

    result = engine.analyze(holdings)

    assert result.sector_concentration_risk is True
    assert result.dominant_sector == "IT"


def test_max_position_weight_is_reported():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 45.0, 20.0, -8.0),
        make_holding("HDFCBANK", "BANK", 25.0, 18.0, -6.0),
        make_holding("MARUTI", "AUTO", 30.0, 20.0, -7.0),
    ]

    result = engine.analyze(holdings)

    assert result.max_position_weight == 45.0


def test_average_volatility_is_reported():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 50.0, 20.0, -8.0),
        make_holding("HDFCBANK", "BANK", 50.0, 30.0, -10.0),
    ]

    result = engine.analyze(holdings)

    assert result.average_volatility == 25.0


def test_max_drawdown_is_reported():
    engine = PortfolioRiskEngine()

    holdings = [
        make_holding("TCS", "IT", 40.0, 20.0, -8.0),
        make_holding("HDFCBANK", "BANK", 30.0, 18.0, -15.0),
        make_holding("MARUTI", "AUTO", 30.0, 22.0, -10.0),
    ]

    result = engine.analyze(holdings)

    assert result.max_drawdown == -15.0


def test_empty_portfolio():
    engine = PortfolioRiskEngine()

    result = engine.analyze([])

    assert isinstance(result, PortfolioRiskSnapshot)
    assert result.risk_score == 0
    assert result.risk_classification == "LOW"
    assert result.holding_count == 0


def test_none_holdings_are_ignored():
    engine = PortfolioRiskEngine()

    holdings = [
        None,
        make_holding("TCS", "IT", 100.0, 20.0, -5.0),
        None,
    ]

    result = engine.analyze(holdings)

    assert result.holding_count == 1
    assert result.max_position_weight == 100.0