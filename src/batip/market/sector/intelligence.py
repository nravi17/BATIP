"""
BATIP Sector Intelligence.

Combines sector strength and sector rotation into one
deterministic sector intelligence snapshot.
"""

from dataclasses import dataclass

from batip.market.sector import SectorSnapshot
from .strength import SectorStrengthEngine
from .rotation import SectorRotation, SectorRotationEngine


@dataclass(frozen=True)
class SectorIntelligenceSnapshot:
    """Consolidated sector intelligence."""

    sectors: list[SectorSnapshot]

    strongest_sector: str | None
    weakest_sector: str | None

    bullish_count: int
    bearish_count: int
    neutral_count: int

    total_score: int
    average_score: float

    sector_bias: str

    rotation_leaders: list[str]
    rotation_improving: list[str]
    rotation_emerging: list[str]
    rotation_weakening: list[str]
    rotation_lagging: list[str]

    confidence: float


class SectorIntelligenceEngine:
    """Combine sector strength and rotation intelligence."""

    def __init__(self) -> None:
        self.strength_engine = SectorStrengthEngine()
        self.rotation_engine = SectorRotationEngine()

    @staticmethod
    def _confidence(
        current: list[SectorSnapshot],
        previous: list[SectorSnapshot],
    ) -> float:
        """
        Calculate deterministic confidence.

        Confidence is based on the availability of current and
        historical sector observations.
        """

        if not current:
            return 0.0

        current_count = len(current)

        if not previous:
            return 70.0

        previous_symbols = {
            sector.symbol
            for sector in previous
            if sector is not None
        }

        matched = sum(
            1
            for sector in current
            if sector is not None
            and sector.symbol in previous_symbols
        )

        coverage = matched / current_count

        return round(70.0 + (coverage * 30.0), 2)

    def analyze(
        self,
        current: list[SectorSnapshot],
        previous: list[SectorSnapshot] | None = None,
    ) -> SectorIntelligenceSnapshot:
        """
        Build consolidated sector intelligence.

        Existing sector snapshots are not mutated.
        """

        current = [
            sector
            for sector in (current or [])
            if sector is not None
        ]

        previous = [
            sector
            for sector in (previous or [])
            if sector is not None
        ]

        if not current:
            return SectorIntelligenceSnapshot(
                sectors=[],
                strongest_sector=None,
                weakest_sector=None,
                bullish_count=0,
                bearish_count=0,
                neutral_count=0,
                total_score=0,
                average_score=0.0,
                sector_bias="Neutral",
                rotation_leaders=[],
                rotation_improving=[],
                rotation_emerging=[],
                rotation_weakening=[],
                rotation_lagging=[],
                confidence=0.0,
            )

        # First normalize current sector scores from change_percent.
        strength = self.strength_engine.analyze(current)

        # Normalize previous sector scores too.
        previous_strength = (
            self.strength_engine.analyze(previous)
            if previous
            else None
        )

        normalized_current = strength.sectors

        normalized_previous = (
            previous_strength.sectors
            if previous_strength is not None
            else []
        )

        rotation = self.rotation_engine.analyze(
            normalized_current,
            normalized_previous,
        )

        rotation_leaders: list[str] = []
        rotation_improving: list[str] = []
        rotation_emerging: list[str] = []
        rotation_weakening: list[str] = []
        rotation_lagging: list[str] = []

        for item in rotation.sectors:
            if item.rotation == SectorRotation.LEADING:
                rotation_leaders.append(item.symbol)

            elif item.rotation == SectorRotation.IMPROVING:
                rotation_improving.append(item.symbol)

            elif item.rotation == SectorRotation.EMERGING:
                rotation_emerging.append(item.symbol)

            elif item.rotation == SectorRotation.WEAKENING:
                rotation_weakening.append(item.symbol)

            elif item.rotation == SectorRotation.LAGGING:
                rotation_lagging.append(item.symbol)

        confidence = self._confidence(
            current,
            previous,
        )

        return SectorIntelligenceSnapshot(
            sectors=normalized_current,
            strongest_sector=strength.strongest_sector,
            weakest_sector=strength.weakest_sector,
            bullish_count=strength.bullish_count,
            bearish_count=strength.bearish_count,
            neutral_count=strength.neutral_count,
            total_score=strength.total_score,
            average_score=strength.average_score,
            sector_bias=strength.bias,
            rotation_leaders=rotation_leaders,
            rotation_improving=rotation_improving,
            rotation_emerging=rotation_emerging,
            rotation_weakening=rotation_weakening,
            rotation_lagging=rotation_lagging,
            confidence=confidence,
        )
