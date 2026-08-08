"""
BATIP Sector Intelligence.

Analyzes normalized sector snapshots and ranks sectors
by daily performance.

This module does not fetch market data and does not
place trades.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class SectorSnapshot:
    """Normalized sector market data."""

    symbol: str
    name: str
    change_percent: float = 0.0
    volume: float = 0.0
    direction: str = "Neutral"
    score: int = 0


class SectorScanner:
    """Analyze and rank market sectors."""

    @staticmethod
    def score_sector(change_percent: float) -> int:
        """Convert sector performance into a deterministic score."""

        if change_percent >= 1.0:
            return 2

        if change_percent > 0:
            return 1

        if change_percent <= -1.0:
            return -2

        if change_percent < 0:
            return -1

        return 0

    @staticmethod
    def direction_from_score(score: int) -> str:
        """Convert score into sector direction."""

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    def analyze(
        self,
        sectors: list[SectorSnapshot],
    ) -> list[SectorSnapshot]:
        """Score and rank sectors by performance."""

        analyzed: list[SectorSnapshot] = []

        for sector in sectors:
            score = self.score_sector(
                sector.change_percent
            )

            analyzed.append(
                SectorSnapshot(
                    symbol=sector.symbol,
                    name=sector.name,
                    change_percent=sector.change_percent,
                    volume=sector.volume,
                    direction=self.direction_from_score(score),
                    score=score,
                )
            )

        return sorted(
            analyzed,
            key=lambda sector: sector.change_percent,
            reverse=True,
        )

    @staticmethod
    def strongest(
        sectors: list[SectorSnapshot],
    ) -> SectorSnapshot | None:
        """Return the strongest sector."""

        if not sectors:
            return None

        return max(
            sectors,
            key=lambda sector: sector.change_percent,
        )

    @staticmethod
    def weakest(
        sectors: list[SectorSnapshot],
    ) -> SectorSnapshot | None:
        """Return the weakest sector."""

        if not sectors:
            return None

        return min(
            sectors,
            key=lambda sector: sector.change_percent,
        )