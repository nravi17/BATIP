"""
BATIP Market Regime Intelligence.

Classifies the overall market regime using market score,
sector breadth, and leading stock strength.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketRegimeSnapshot:
    """Normalized market regime intelligence."""

    regime: str
    risk_state: str
    breadth: str
    confidence: float


class MarketRegimeEngine:
    """Classify the overall market regime."""

    @staticmethod
    def classify_regime(market_score: int) -> str:
        """Classify market direction."""

        if market_score > 0:
            return "BULLISH"

        if market_score < 0:
            return "BEARISH"

        return "NEUTRAL"

    @staticmethod
    def classify_risk_state(
        market_score: int,
        top_stock_score: int,
    ) -> str:
        """Classify risk appetite."""

        if market_score > 0 and top_stock_score > 0:
            return "RISK_ON"

        return "RISK_OFF"

    @staticmethod
    def classify_breadth(
        bullish_sectors: int,
        bearish_sectors: int,
    ) -> str:
        """Classify sector market breadth."""

        if bullish_sectors > bearish_sectors:
            return "POSITIVE"

        if bearish_sectors > bullish_sectors:
            return "NEGATIVE"

        return "NEUTRAL"

    @staticmethod
    def calculate_confidence(
        market_score: int,
        bullish_sectors: int,
        bearish_sectors: int,
        top_stock_score: int,
    ) -> float:
        """Calculate deterministic regime confidence."""

        total_sectors = bullish_sectors + bearish_sectors

        if total_sectors == 0:
            breadth_alignment = 0.0
        else:
            breadth_alignment = (
                abs(bullish_sectors - bearish_sectors)
                / total_sectors
            )

        score_alignment = min(
            abs(market_score) / 10.0,
            1.0,
        )

        stock_alignment = min(
            abs(top_stock_score) / 10.0,
            1.0,
        )

        confidence = (
            breadth_alignment * 40.0
            + score_alignment * 35.0
            + stock_alignment * 25.0
        )

        return round(confidence, 2)

    def analyze(
        self,
        market_score: int,
        bullish_sectors: int,
        bearish_sectors: int,
        top_stock_score: int,
    ) -> MarketRegimeSnapshot:
        """Analyze overall market regime."""

        regime = self.classify_regime(market_score)

        risk_state = self.classify_risk_state(
            market_score=market_score,
            top_stock_score=top_stock_score,
        )

        breadth = self.classify_breadth(
            bullish_sectors=bullish_sectors,
            bearish_sectors=bearish_sectors,
        )

        confidence = self.calculate_confidence(
            market_score=market_score,
            bullish_sectors=bullish_sectors,
            bearish_sectors=bearish_sectors,
            top_stock_score=top_stock_score,
        )

        return MarketRegimeSnapshot(
            regime=regime,
            risk_state=risk_state,
            breadth=breadth,
            confidence=confidence,
        )