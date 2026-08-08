"""
BATIP Market Breadth Analyzer.

Analyzes advances, declines, and unchanged securities
to determine overall market breadth.

This module does not fetch market data and does not
place trades.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class BreadthResult:
    """Normalized market breadth result."""

    advances: int = 0
    declines: int = 0
    unchanged: int = 0

    advance_decline_ratio: float = 0.0

    score: int = 0

    signal: str = "Neutral"

    description: str = ""


class BreadthAnalyzer:
    """Calculate and classify market breadth."""

    @staticmethod
    def calculate(
        advances: int,
        declines: int,
        unchanged: int = 0,
    ) -> BreadthResult:
        """Calculate market breadth."""

        advances = max(0, int(advances))
        declines = max(0, int(declines))
        unchanged = max(0, int(unchanged))

        if declines == 0:
            ratio = float(advances) if advances > 0 else 0.0
        else:
            ratio = advances / declines

        score = BreadthAnalyzer._score(
            advances,
            declines,
        )

        signal, description = BreadthAnalyzer._classify(
            score,
            ratio,
        )

        return BreadthResult(
            advances=advances,
            declines=declines,
            unchanged=unchanged,
            advance_decline_ratio=round(ratio, 2),
            score=score,
            signal=signal,
            description=description,
        )

    @staticmethod
    def _score(
        advances: int,
        declines: int,
    ) -> int:
        """Convert breadth into a deterministic score."""

        total = advances + declines

        if total == 0:
            return 0

        advance_percentage = (
            advances / total
        ) * 100

        if advance_percentage >= 70:
            return 2

        if advance_percentage >= 55:
            return 1

        if advance_percentage <= 30:
            return -2

        if advance_percentage < 45:
            return -1

        return 0

    @staticmethod
    def _classify(
        score: int,
        ratio: float,
    ) -> tuple[str, str]:
        """Convert breadth score into a market signal."""

        if score == 2:
            return (
                "Strong Bullish",
                f"Strong market breadth with A/D ratio "
                f"{ratio:.2f}.",
            )

        if score == 1:
            return (
                "Bullish",
                f"Positive market breadth with A/D ratio "
                f"{ratio:.2f}.",
            )

        if score == -2:
            return (
                "Strong Bearish",
                f"Very weak market breadth with A/D ratio "
                f"{ratio:.2f}.",
            )

        if score == -1:
            return (
                "Bearish",
                f"Negative market breadth with A/D ratio "
                f"{ratio:.2f}.",
            )

        return (
            "Neutral",
            f"Mixed market breadth with A/D ratio "
            f"{ratio:.2f}.",
        )