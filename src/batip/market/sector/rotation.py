"""
BATIP Sector Rotation Intelligence.

Compares current sector strength against previous sector strength
to identify sector rotation.
"""

from dataclasses import dataclass

from batip.market.sector import SectorSnapshot


@dataclass(frozen=True)
class SectorRotationItem:
    """Rotation classification for a sector."""

    symbol: str
    name: str
    current_score: int
    previous_score: int
    score_change: int

    current_change_percent: float
    previous_change_percent: float

    rotation: str


@dataclass(frozen=True)
class SectorRotationSnapshot:
    """Complete sector rotation analysis."""

    sectors: list[SectorRotationItem]


class SectorRotation:
    """Constants for sector rotation states."""

    LEADING = "Leading"
    IMPROVING = "Improving"
    EMERGING = "Emerging"
    WEAKENING = "Weakening"
    LAGGING = "Lagging"
    NEUTRAL = "Neutral"


class SectorRotationEngine:
    """Analyze sector rotation using current and previous strength."""

    @staticmethod
    def score_change(
        current: SectorSnapshot,
        previous: SectorSnapshot,
    ) -> int:
        """
        Calculate change in sector score.

        Positive value:
            sector strength improved.

        Negative value:
            sector strength deteriorated.

        Zero:
            sector strength unchanged.
        """
        return int(current.score) - int(previous.score)

    @staticmethod
    def classify(
        current: SectorSnapshot,
        previous: SectorSnapshot,
    ) -> str:
        """
        Classify sector rotation.

        Rules:

        Leading:
            Current sector is strongly bullish and
            remains at the same strong level.

        Improving:
            Sector strength has improved and is now bullish.

        Emerging:
            Sector is moving from bearish/neutral toward bullish
            but has not yet become strongly bullish.

        Weakening:
            Sector strength has deteriorated.

        Lagging:
            Sector remains strongly bearish.

        Neutral:
            No meaningful rotation.
        """

        current_score = int(current.score)
        previous_score = int(previous.score)

        score_change = current_score - previous_score

        # Strong bullish sector maintaining strength.
        if current_score >= 2 and previous_score >= 2:
            return SectorRotation.LEADING

        # Strong bearish sector maintaining weakness.
        if current_score <= -2 and previous_score <= -2:
            return SectorRotation.LAGGING

        # Moving positively into bullish territory.
        if score_change > 0:
            if current_score > 0:
                return SectorRotation.IMPROVING

            # Positive movement but still neutral.
            if current_score == 0:
                return SectorRotation.EMERGING

        # Moving negatively.
        if score_change < 0:
            if current_score < 0:
                return SectorRotation.WEAKENING

            if current_score == 0:
                return SectorRotation.WEAKENING

        return SectorRotation.NEUTRAL

    def analyze(
        self,
        current: list[SectorSnapshot],
        previous: list[SectorSnapshot],
    ) -> SectorRotationSnapshot:
        """
        Compare current and previous sector snapshots.

        Sectors missing from the previous snapshot use a neutral baseline.
        """

        if not current:
            return SectorRotationSnapshot(
                sectors=[],
            )

        previous_map = {
            sector.symbol: sector
            for sector in previous
            if sector is not None
        }

        result: list[SectorRotationItem] = []

        for sector in current:
            if sector is None:
                continue

            old = previous_map.get(sector.symbol)

            # If missing from previous, use neutral baseline
            if old is None:
                old = SectorSnapshot(
                    symbol=sector.symbol,
                    name=sector.name,
                    score=0,
                    change_percent=0.0,
                )

            score_change = self.score_change(
                sector,
                old,
            )

            rotation = self.classify(
                sector,
                old,
            )

            result.append(
                SectorRotationItem(
                    symbol=sector.symbol,
                    name=sector.name,
                    current_score=int(sector.score),
                    previous_score=int(old.score),
                    score_change=score_change,
                    current_change_percent=float(
                        sector.change_percent
                    ),
                    previous_change_percent=float(
                        old.change_percent
                    ),
                    rotation=rotation,
                )
            )

        # Ranking order:
        # 1. current score
        # 2. current change %
        # 3. score change
        # 4. symbol
        result.sort(
            key=lambda item: (
                item.current_score,
                item.current_change_percent,
                item.score_change,
                item.symbol,
            ),
            reverse=True,
        )

        return SectorRotationSnapshot(
            sectors=result,
        )