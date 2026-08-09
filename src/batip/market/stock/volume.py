"""
BATIP Stock Volume Engine.

Provides deterministic volume scoring and
volume confirmation analysis.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockVolumeSnapshot:
    """Normalized stock volume snapshot."""

    symbol: str
    volume_change_percent: float
    average_volume_ratio: float = 1.0
    score: int = 0
    direction: str = "Neutral"
    volume_confirmation: str = "Normal"


class StockVolumeEngine:
    """Analyze stock volume strength and confirmation."""

    @staticmethod
    def score_volume(volume_change_percent: float) -> int:
        """
        Convert volume percentage movement into a normalized score.

        Rules:
            >= +50% -> +2
            >   0%  -> +1
            == 0%   ->  0
            <   0%  -> -1
            <= -50% -> -2
        """

        change = float(volume_change_percent)

        if change >= 50:
            return 2

        if change > 0:
            return 1

        if change <= -50:
            return -2

        if change < 0:
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        """Convert volume score into market direction."""

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def confirmation_from_ratio(
        average_volume_ratio: float,
    ) -> str:
        """
        Classify volume confirmation from average-volume ratio.

        >= 1.5 -> Strong
        >= 1.1 -> Moderate
        <  1.1 -> Normal
        """

        ratio = float(average_volume_ratio)

        if ratio >= 1.5:
            return "Strong"

        if ratio >= 1.1:
            return "Moderate"

        return "Normal"

    def analyze(
        self,
        volume: StockVolumeSnapshot,
    ) -> StockVolumeSnapshot:
        """Analyze a stock volume snapshot."""

        if volume is None:
            raise ValueError("volume cannot be None")

        current_change = float(
            volume.volume_change_percent
        )

        ratio = float(
            volume.average_volume_ratio
        )

        score = self.score_volume(current_change)
        direction = self.direction_from_score(score)

        confirmation = self.confirmation_from_ratio(ratio)

        # Negative volume with a low volume ratio represents
        # weak participation rather than strong bearish confirmation.
        if score < 0 and ratio < 0.75:
            confirmation = "Weak"

        return StockVolumeSnapshot(
            symbol=volume.symbol,
            volume_change_percent=current_change,
            average_volume_ratio=ratio,
            score=score,
            direction=direction,
            volume_confirmation=confirmation,
        )