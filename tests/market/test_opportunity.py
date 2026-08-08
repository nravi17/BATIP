from batip.market.opportunity import OpportunityEngine


def test_strong_bullish_opportunity():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=10,
        technical_score=10,
        market_score=2,
        sector_score=2,
    )

    assert result.opportunity_score == 14
    assert result.recommendation == "STRONG BUY"
    assert result.direction == "Bullish"
    assert result.intraday == "FAVORABLE"
    assert result.overnight == "FAVORABLE"


def test_strong_bearish_opportunity():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=-10,
        technical_score=-10,
        market_score=-2,
        sector_score=-2,
    )

    assert result.opportunity_score == -6
    assert result.recommendation == "SELL"
    assert result.direction == "Bearish"
    assert result.intraday == "WATCH"
    assert result.overnight == "WATCH"


def test_bullish_stock_in_bearish_market_is_downgraded():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=8,
        technical_score=8,
        market_score=-2,
        sector_score=2,
    )

    assert result.opportunity_score < 8
    assert "Market regime is strongly bearish" in result.reasons


def test_weak_stock_in_strong_market_is_downgraded():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=-8,
        technical_score=-8,
        market_score=2,
        sector_score=-2,
    )

    assert result.opportunity_score > -8
    assert result.direction == "Bearish"


def test_strong_sector_supports_stock():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=6,
        technical_score=5,
        market_score=0,
        sector_score=2,
    )

    assert "Strong sector supports the stock" in result.reasons


def test_weak_sector_downgrades_bullish_stock():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=8,
        technical_score=6,
        market_score=0,
        sector_score=-2,
    )

    assert "Strong stock but weak sector" in result.reasons


def test_technical_confirmation():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=6,
        technical_score=8,
        market_score=0,
        sector_score=0,
    )

    assert (
        "Technical signals strongly confirm bullish setup"
        in result.reasons
    )


def test_technical_divergence():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=6,
        technical_score=-6,
        market_score=0,
        sector_score=0,
    )

    assert (
        "Technical signals contradict bullish setup"
        in result.reasons
    )


def test_watch_when_signals_are_mixed():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=2,
        technical_score=0,
        market_score=0,
        sector_score=0,
    )

    assert result.recommendation == "WATCH"
    assert result.direction == "Bullish"


def test_intraday_requires_confirmation():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=5,
        technical_score=1,
        market_score=0,
        sector_score=0,
    )

    assert result.intraday == "WATCH"


def test_overnight_requires_market_alignment():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=8,
        technical_score=8,
        market_score=-1,
        sector_score=1,
    )

    assert result.overnight != "FAVORABLE"


def test_confidence_is_capped():
    engine = OpportunityEngine()

    result = engine.evaluate(
        stock_score=10,
        technical_score=10,
        market_score=2,
        sector_score=2,
    )

    assert result.confidence <= 95.0