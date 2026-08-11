"""
BATIP Sector Snapshot Intelligence.

Creates a deterministic snapshot of sector-level market intelligence.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SectorSnapshot:
    """Sector-level market snapshot."""

    symbol: str = ""
    name: str = ""
    change_percent: float = 0.0

    score: int = 0
    direction: str = "Neutral"

    sector: str = ""
    classification: str = "NEUTRAL"
    market_bias: str = "Neutral"

    breadth_score: int = 0
    momentum_score: int = 0
    confidence: float = 0.0


class SectorSnapshotEngine:
    """Build deterministic sector snapshots."""

    @staticmethod
    def _value(
        data: Any,
        field: str,
        default: Any = 0,
    ) -> Any:
        """Safely extract a value from dictionaries or objects."""

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
    ) -> SectorSnapshot | None:
        """Create a sector snapshot without mutating the input."""

        if data is None:
            return None

        sector = str(
            self._value(data, "sector", "")
        )

        symbol = str(
            self._value(data, "symbol", sector)
        )

        name = str(
            self._value(data, "name", sector)
        )

        change_percent = float(
            self._value(data, "change_percent", 0.0)
        )

        breadth_score = int(
            self._value(data, "breadth_score", 0)
        )

        momentum_score = int(
            self._value(data, "momentum_score", 0)
        )

        confidence = float(
            self._value(data, "confidence", 0.0)
        )

        market_bias = str(
            self._value(data, "market_bias", "Neutral")
        )

        score = breadth_score + momentum_score

        # If explicit breadth/momentum scores are unavailable,
        # derive the normalized sector score from market movement.
        if (
            breadth_score == 0
            and momentum_score == 0
            and change_percent != 0
        ):
            if change_percent >= 1.0:
                score = 2
            elif change_percent > 0:
                score = 1
            elif change_percent <= -1.0:
                score = -2
            else:
                score = -1

        direction = (
            "Bullish"
            if score > 0
            else "Bearish"
            if score < 0
            else "Neutral"
        )

        return SectorSnapshot(
            symbol=symbol,
            name=name,
            change_percent=change_percent,
            score=score,
            direction=direction,
            sector=sector,
            classification=self.classify(
                breadth_score + momentum_score
            ),
            market_bias=market_bias,
            breadth_score=breadth_score,
            momentum_score=momentum_score,
            confidence=confidence,
        )
