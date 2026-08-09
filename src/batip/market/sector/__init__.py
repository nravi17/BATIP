"""
BATIP Sector Intelligence.

Provides deterministic sector scoring and ranking.
"""

from dataclasses import dataclass


@dataclass
class SectorSnapshot:
    """
    Normalized snapshot for a market sector.
    """

    symbol: str
    name: str
    change_percent: float
    score: int = 0
    direction: str = "Neutral"


class SectorScanner:
    """
    Analyze and rank market sectors.
    """

    @staticmethod
    def score_sector(change_percent: float) -> int:
        """
        Convert sector percentage movement into a normalized score.

        Rules:
            >= +1.0% -> +2
            >   0%   -> +1
            == 0%    ->  0
            <   0%   -> -1
            <= -1.0% -> -2
        """

        change = float(change_percent)

        if change >= 1.0:
            return 2

        if change > 0:
            return 1

        if change <= -1.0:
            return -2

        if change < 0:
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        """
        Convert normalized sector score into direction.
        """

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    def analyze(
        self,
        sectors: list[SectorSnapshot],
    ) -> list[SectorSnapshot]:
        """
        Score and rank supplied sectors.

        Existing SectorSnapshot objects are not mutated.

        Results are ordered from strongest to weakest based on:
            1. score
            2. percentage change
            3. symbol
        """

        if not sectors:
            return []

        analyzed: list[SectorSnapshot] = []

        for sector in sectors:
            if sector is None:
                continue

            score = self.score_sector(sector.change_percent)
            direction = self.direction_from_score(score)

            analyzed.append(
                SectorSnapshot(
                    symbol=sector.symbol,
                    name=sector.name,
                    change_percent=sector.change_percent,
                    score=score,
                    direction=direction,
                )
            )

        analyzed.sort(
            key=lambda sector: (
                sector.score,
                sector.change_percent,
                sector.symbol,
            ),
            reverse=True,
        )

        return analyzed

    @staticmethod
    def strongest(
        sectors: list[SectorSnapshot],
    ) -> SectorSnapshot | None:
        """
        Return the strongest sector.
        """

        if not sectors:
            return None

        return max(
            sectors,
            key=lambda sector: (
                sector.score,
                sector.change_percent,
            ),
        )

    @staticmethod
    def weakest(
        sectors: list[SectorSnapshot],
    ) -> SectorSnapshot | None:
        """
        Return the weakest sector.
        """

        if not sectors:
            return None

        return min(
            sectors,
            key=lambda sector: (
                sector.score,
                sector.change_percent,
            ),
        )

from .strength import (
    SectorStrengthEngine,
    SectorStrengthSnapshot,
)

from .rotation import (
    SectorRotation,
    SectorRotationEngine,
    SectorRotationItem,
    SectorRotationSnapshot,
)

__all__ = [
    "SectorScanner",
    "SectorSnapshot",
    "SectorStrengthEngine",
    "SectorStrengthSnapshot",
    "SectorRotation",
    "SectorRotationEngine",
    "SectorRotationItem",
    "SectorRotationSnapshot",
]