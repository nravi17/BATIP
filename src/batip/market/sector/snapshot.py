"""
BATIP Sector Snapshot Intelligence.

Creates a deterministic snapshot of sector-level market intelligence.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SectorIntelligenceSnapshot:
    """Sector-level market snapshot."""

    sector: str
    score: int
    classification: str
    market_bias: str
    breadth_score: int
    momentum_score: int
    confidence: float


class SectorSnapshotEngine:
    """Build deterministic sector snapshots."""

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from dicts or objects."""

        if isinstance(data, dict):
            return data.get(field, default)

        return getattr(data, field, default)

    @staticmethod
    def classify(score: int) -> str:
        """Classify sector strength."""

        if score >= 8:
            return "STRONG"

        if score >= 3:
            return "POSITIVE"

        if score <= -8:
            return "VERY WEAK"

        if score < 0:
            return "WEAK"

        return "NEUTRAL"

    def analyze(
        self,
        data: Any,
    ) -> SectorIntelligenceSnapshot | None:
        """Create a sector snapshot without mutating the input."""

        if data is None:
            return None

        sector = str(
            self._value(data, "sector", "")
        )

        breadth_score = int(
            self._value(data, "breadth_score", 0)
        )

        momentum_score = int(
            self._value(data, "momentum_score", 0)
        )

        confidence = float(
            self._value(data, "confidence", 0)
        )

        market_bias = str(
            self._value(data, "market_bias", "Neutral")
        )

        score = breadth_score + momentum_score

        return SectorIntelligenceSnapshot(
            sector=sector,
            score=score,
            classification=self.classify(score),
            market_bias=market_bias,
            breadth_score=breadth_score,
            momentum_score=momentum_score,
            confidence=confidence,
        )
