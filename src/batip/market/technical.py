"""
BATIP Technical Intelligence.

Provider-independent technical signal calculations.

This module does not fetch market data and does not place trades.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TechnicalSnapshot:
    """Derived technical characteristics for a stock."""

    trend_score: int = 0
    momentum_score: int = 0
    breakout_score: int = 0
    relative_strength_score: int = 0
    volume_score: int = 0

    score: int = 0
    direction: str = "Neutral"
    confidence: float = 0.0


class TechnicalScanner:
    """Convert technical inputs into a deterministic signal."""

    @staticmethod
    def trend_score(
        price: float,
        short_ma: float,
        long_ma: float,
    ) -> int:
        """
        Score price/Moving Average alignment.

        +2 = price above both MAs and short MA above long MA
        +1 = bullish partial alignment
         0 = mixed
        -1 = bearish partial alignment
        -2 = fully bearish alignment
        """

        if (
            price > short_ma
            and short_ma > long_ma
        ):
            return 2

        if price > short_ma:
            return 1

        if (
            price < short_ma
            and short_ma < long_ma
        ):
            return -2

        if price < short_ma:
            return -1

        return 0

    @staticmethod
    def momentum_score(momentum: float) -> int:
        """Score normalized momentum."""

        if momentum >= 2.0:
            return 2

        if momentum > 0:
            return 1

        if momentum <= -2.0:
            return -2

        if momentum < 0:
            return -1

        return 0

    @staticmethod
    def breakout_score(
        price: float,
        resistance: float,
        support: float,
    ) -> int:
        """Detect confirmed directional price breaks."""

        if price > resistance:
            return 2

        if price < support:
            return -2

        return 0

    @staticmethod
    def relative_strength_score(
        stock_change_percent: float,
        benchmark_change_percent: float,
    ) -> int:
        """Compare stock performance with its benchmark."""

        difference = (
            stock_change_percent
            - benchmark_change_percent
        )

        if difference >= 2.0:
            return 2

        if difference > 0:
            return 1

        if difference <= -2.0:
            return -2

        if difference < 0:
            return -1

        return 0

    @staticmethod
    def volume_confirmation_score(
        price_change_percent: float,
        volume_change_percent: float,
    ) -> int:
        """
        Score price/volume confirmation.

        Positive price + increasing volume = bullish.
        Negative price + increasing volume = bearish.
        Weakening volume reduces confirmation.
        """

        if (
            price_change_percent > 0
            and volume_change_percent >= 50
        ):
            return 2

        if (
            price_change_percent > 0
            and volume_change_percent > 0
        ):
            return 1

        if (
            price_change_percent < 0
            and volume_change_percent >= 50
        ):
            return -2

        if (
            price_change_percent < 0
            and volume_change_percent > 0
        ):
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def confidence_from_score(score: int) -> float:
        """
        Convert technical agreement into confidence.

        Maximum possible score is +/-10.
        """

        confidence = 50.0 + (
            abs(score) * 5.0
        )

        return min(95.0, confidence)

    def analyze(
        self,
        *,
        price: float,
        short_ma: float,
        long_ma: float,
        momentum: float,
        resistance: float,
        support: float,
        stock_change_percent: float,
        benchmark_change_percent: float,
        volume_change_percent: float,
    ) -> TechnicalSnapshot:
        """Build a complete technical snapshot."""

        trend = self.trend_score(
            price,
            short_ma,
            long_ma,
        )

        momentum_result = self.momentum_score(
            momentum
        )

        breakout = self.breakout_score(
            price,
            resistance,
            support,
        )

        relative_strength = (
            self.relative_strength_score(
                stock_change_percent,
                benchmark_change_percent,
            )
        )

        volume = self.volume_confirmation_score(
            stock_change_percent,
            volume_change_percent,
        )

        score = (
            trend
            + momentum_result
            + breakout
            + relative_strength
            + volume
        )

        return TechnicalSnapshot(
            trend_score=trend,
            momentum_score=momentum_result,
            breakout_score=breakout,
            relative_strength_score=relative_strength,
            volume_score=volume,
            score=score,
            direction=self.direction_from_score(score),
            confidence=self.confidence_from_score(score),
        )