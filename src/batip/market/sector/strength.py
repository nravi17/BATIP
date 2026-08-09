"""
BATIP Sector Strength Engine.

Aggregates scored sector snapshots into higher-level
sector strength intelligence.
"""

from dataclasses import dataclass

from . import SectorSnapshot


@dataclass(frozen=True)
class SectorStrengthSnapshot:
    """Aggregated sector strength intelligence."""

    sectors: list[SectorSnapshot]

    strongest_sector: str | None
    weakest_sector: str | None

    bullish_count: int
    bearish_count: int
    neutral_count: int

    total_score: int
    average_score: float

    bias: str


class SectorStrengthEngine:
    """Analyze overall strength across market sectors."""

    @staticmethod
    def classify_bias(
        total_score: int,
        bullish_count: int,
        bearish_count: int,
    ) -> str:
        """Determine the overall sector bias."""

        if (
            total_score >= 4
            and bullish_count > bearish_count
        ):
            return "Strong Bullish"

        if (
            total_score <= -4
            and bearish_count > bullish_count
        ):
            return "Strong Bearish"

        if (
            total_score > 0
            and bullish_count > bearish_count
        ):
            return "Bullish"

        if (
            total_score < 0
            and bearish_count > bullish_count
        ):
            return "Bearish"

        return "Neutral"

    def analyze(
        self,
        sectors: list[SectorSnapshot],
    ) -> SectorStrengthSnapshot:
        """Aggregate sector strength information."""

        valid_sectors = [
            sector
            for sector in sectors
            if sector is not None
        ]

        if not valid_sectors:
            return SectorStrengthSnapshot(
                sectors=[],
                strongest_sector=None,
                weakest_sector=None,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
                total_score=0,
                average_score=0.0,
                bias="Neutral",
            )

        # SectorScanner is imported locally to avoid circular
        # initialization issues inside the sector package.
        from . import SectorScanner

        scanner = SectorScanner()

        analyzed = scanner.analyze(valid_sectors)

        if not analyzed:
            return SectorStrengthSnapshot(
                sectors=[],
                strongest_sector=None,
                weakest_sector=None,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
                total_score=0,
                average_score=0.0,
                bias="Neutral",
            )

        bullish_count = sum(
            1
            for sector in analyzed
            if sector.score > 0
        )

        bearish_count = sum(
            1
            for sector in analyzed
            if sector.score < 0
        )

        neutral_count = sum(
            1
            for sector in analyzed
            if sector.score == 0
        )

        total_score = sum(
            sector.score
            for sector in analyzed
        )

        average_score = total_score / len(analyzed)

        strongest = scanner.strongest(analyzed)
        weakest = scanner.weakest(analyzed)

        bias = self.classify_bias(
            total_score=total_score,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
        )

        return SectorStrengthSnapshot(
            sectors=analyzed,
            strongest_sector=(
                strongest.symbol
                if strongest is not None
                else None
            ),
            weakest_sector=(
                weakest.symbol
                if weakest is not None
                else None
            ),
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            total_score=total_score,
            average_score=average_score,
            bias=bias,
        )