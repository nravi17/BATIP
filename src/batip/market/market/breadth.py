"""
BATIP Market Breadth Intelligence.

Provides deterministic advance/decline analysis and breadth scoring.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketBreadthSnapshot:
    """Normalized market breadth snapshot."""

    advances: int
    declines: int
    unchanged: int

    total_stocks: int = 0
    advance_percent: float = 0.0
    decline_percent: float = 0.0
    ad_ratio: float = 0.0

    score: int = 0
    direction: str = "Neutral"
    breadth_status: str = "Neutral"


class MarketBreadthEngine:
    """Analyze market advance/decline breadth."""

    @staticmethod
    def calculate_ad_ratio(
        advances: int,
        declines: int,
    ) -> float:
        """Calculate advance/decline ratio."""

        advances = int(advances)
        declines = int(declines)

        if declines == 0:
            if advances > 0:
                return float("inf")
            return 0.0

        return advances / declines

    @staticmethod
    def calculate_percent(
        value: int,
        total: int,
    ) -> float:
        """Calculate percentage of total stocks."""

        if total <= 0:
            return 0.0

        return (value / total) * 100.0

    @staticmethod
    def breadth_score(
        advance_percent: float,
        decline_percent: float,
    ) -> int:
        """
        Convert breadth into a normalized score.

        Rules:
            >= 70% advances -> +2
            >= 55% advances -> +1
            otherwise balanced -> 0
            >= 55% declines -> -1
            >= 70% declines -> -2
        """

        advance_percent = float(advance_percent)
        decline_percent = float(decline_percent)

        if advance_percent >= 70:
            return 2

        if advance_percent >= 55:
            return 1

        if decline_percent >= 70:
            return -2

        if decline_percent >= 55:
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        """Convert breadth score into market direction."""

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def status_from_score(score: int) -> str:
        """Convert breadth score into human-readable status."""

        if score >= 2:
            return "Strong Positive Breadth"

        if score == 1:
            return "Positive Breadth"

        if score == -1:
            return "Negative Breadth"

        if score <= -2:
            return "Strong Negative Breadth"

        return "Neutral Breadth"

    def analyze(
        self,
        advances: int,
        declines: int,
        unchanged: int = 0,
    ) -> MarketBreadthSnapshot:
        """Analyze market breadth."""

        advances = max(0, int(advances))
        declines = max(0, int(declines))
        unchanged = max(0, int(unchanged))

        total = advances + declines + unchanged

        advance_percent = self.calculate_percent(
            advances,
            total,
        )

        decline_percent = self.calculate_percent(
            declines,
            total,
        )

        ad_ratio = self.calculate_ad_ratio(
            advances,
            declines,
        )

        score = self.breadth_score(
            advance_percent,
            decline_percent,
        )

        return MarketBreadthSnapshot(
            advances=advances,
            declines=declines,
            unchanged=unchanged,
            total_stocks=total,
            advance_percent=advance_percent,
            decline_percent=decline_percent,
            ad_ratio=ad_ratio,
            score=score,
            direction=self.direction_from_score(score),
            breadth_status=self.status_from_score(score),
        )