"""
BATIP Market Scanner.

Evaluates normalized market indices and breadth to determine:

- normalized index scores
- market direction
- market regime
- strongest / weakest index
- market confidence

This module does not place trades.
"""

from __future__ import annotations

from batip.market.models import (
    IndexSnapshot,
    MarketBreadth,
    MarketDirection,
    MarketRegime,
    MarketSnapshot,
)


class MarketScanner:
    """Analyze market indices and optional market breadth."""

    # ------------------------------------------------------------------
    # INDEX SCORING
    # ------------------------------------------------------------------

    @staticmethod
    def score_index(index: IndexSnapshot) -> int:
        """
        Convert percentage movement into a normalized index score.

        Rules:
            >= +1.0%  -> +2
            >   0%    -> +1
            == 0%     ->  0
            <   0%    -> -1
            <= -1.0%  -> -2

        The existing ``index.score`` field is deliberately ignored.
        The scanner owns the normalized scoring rules.
        """

        change = float(index.change_percent)

        if change >= 1.0:
            return 2

        if change > 0:
            return 1

        if change <= -1.0:
            return -2

        if change < 0:
            return -1

        return 0

    # ------------------------------------------------------------------
    # SCORE -> DIRECTION
    # ------------------------------------------------------------------

    @staticmethod
    def direction_from_score(score: int) -> MarketDirection:
        """Convert a numeric score into a market direction."""

        if score > 0:
            return MarketDirection.BULLISH

        if score < 0:
            return MarketDirection.BEARISH

        return MarketDirection.NEUTRAL

    # ------------------------------------------------------------------
    # SCORE -> REGIME
    # ------------------------------------------------------------------

    @staticmethod
    def regime_from_score(score: int) -> MarketRegime:
        """
        Convert aggregate score into a market regime.

        Rules:
            >= +5 -> Strong Bullish
            >= +2 -> Bullish
            <= -5 -> Strong Bearish
            <= -2 -> Bearish
            otherwise Neutral
        """

        if score >= 5:
            return MarketRegime.STRONG_BULLISH

        if score >= 2:
            return MarketRegime.BULLISH

        if score <= -5:
            return MarketRegime.STRONG_BEARISH

        if score <= -2:
            return MarketRegime.BEARISH

        return MarketRegime.NEUTRAL

    # ------------------------------------------------------------------
    # BREADTH SCORING
    # ------------------------------------------------------------------

    @staticmethod
    def score_breadth(breadth: MarketBreadth | None) -> int:
        """
        Convert breadth into a normalized contribution.

        Breadth is intentionally capped at +/-2.

        Logic:
            Bullish breadth → +2
            Bearish breadth → -2
            Neutral or None → 0
        """

        if breadth is None:
            return 0

        if breadth.direction == MarketDirection.BULLISH:
            return 2

        if breadth.direction == MarketDirection.BEARISH:
            return -2

        return 0

    # ------------------------------------------------------------------
    # INDEX AGGREGATION
    # ------------------------------------------------------------------

    @classmethod
    def index_contribution(
        cls,
        indices: list[IndexSnapshot],
        *,
        breadth_available: bool,
    ) -> int:
        """
        Calculate normalized contribution from indices.

        With breadth available:
            Every index contributes its normalized score.

        Without breadth:
            The aggregate is deliberately conservative.
        """

        total = sum(cls.score_index(index) for index in indices)

        if breadth_available:
            return total

        # Conservative index-only signal.
        if total > 0:
            return 2

        if total < 0:
            return -2

        return 0

    # ------------------------------------------------------------------
    # MAIN SCANNER
    # ------------------------------------------------------------------

    def scan(
        self,
        indices: list[IndexSnapshot] | None = None,
        breadth: MarketBreadth | None = None,
        timestamp: str | None = None,
    ) -> MarketSnapshot:
        """
        Analyze supplied indices and optional breadth.

        Existing IndexSnapshot objects are never mutated.

        None entries are ignored.

        If no valid indices are supplied, a neutral/unavailable
        MarketSnapshot is returned.
        """

        # --------------------------------------------------------------
        # Normalize input
        # --------------------------------------------------------------

        if indices is None:
            indices = []

        valid_indices = [
            index
            for index in indices
            if index is not None
        ]

        # --------------------------------------------------------------
        # Empty market
        # --------------------------------------------------------------

        if not valid_indices:
            return MarketSnapshot(
                indices=[],
                breadth=breadth,
                regime=MarketRegime.NEUTRAL,
                score=0,
                strongest_index=None,
                weakest_index=None,
                status=MarketSnapshot().status,
                timestamp=timestamp,
                reasons=[
                    "No index data available.",
                ],
            )

        # --------------------------------------------------------------
        # Normalize every index score
        # --------------------------------------------------------------

        analyzed: list[IndexSnapshot] = []

        for index in valid_indices:
            normalized_score = self.score_index(index)

            analyzed.append(
                IndexSnapshot(
                    symbol=index.symbol,
                    name=index.name,
                    value=index.value,
                    change=index.change,
                    change_percent=index.change_percent,
                    previous_close=index.previous_close,
                    day_open=index.day_open,
                    day_high=index.day_high,
                    day_low=index.day_low,
                    direction=self.direction_from_score(
                        normalized_score
                    ),
                    score=normalized_score,
                    status=index.status,
                    timestamp=index.timestamp,
                    metadata=dict(index.metadata),
                )
            )

        # --------------------------------------------------------------
        # Strongest / weakest index
        # --------------------------------------------------------------

        strongest = max(
            analyzed,
            key=lambda index: index.change_percent,
        )

        weakest = min(
            analyzed,
            key=lambda index: index.change_percent,
        )

        # --------------------------------------------------------------
        # Index contribution
        # --------------------------------------------------------------

        index_score = self.index_contribution(
            analyzed,
            breadth_available=breadth is not None,
        )

        # --------------------------------------------------------------
        # Breadth contribution
        # --------------------------------------------------------------

        breadth_score = self.score_breadth(breadth)

        # --------------------------------------------------------------
        # Final market score
        # --------------------------------------------------------------

        total_score = index_score + breadth_score

        # --------------------------------------------------------------
        # Market regime
        # --------------------------------------------------------------

        regime = self.regime_from_score(total_score)

        # --------------------------------------------------------------
        # Reasons
        # --------------------------------------------------------------

        reasons: list[str] = []

        reasons.append(
            f"Index contribution: {index_score}"
        )

        if breadth is None:
            reasons.append(
                "Breadth data unavailable"
            )
        else:
            reasons.append(
                f"Breadth contribution: {breadth_score}"
            )

        if total_score > 0:
            reasons.append(
                "Market conditions currently favor bullish direction"
            )

        elif total_score < 0:
            reasons.append(
                "Market conditions currently favor bearish direction"
            )

        else:
            reasons.append(
                "Market conditions are currently neutral"
            )

        if breadth is not None:
            index_direction = self.direction_from_score(index_score)

            if (
                breadth.direction == index_direction
                and breadth.direction != MarketDirection.NEUTRAL
            ):
                reasons.append(
                    f"Market breadth confirms "
                    f"{breadth.direction.value.lower()} participation"
                )

            elif breadth.direction == MarketDirection.NEUTRAL:
                reasons.append(
                    "Market breadth is neutral"
                )

            else:
                reasons.append(
                    "Market breadth diverges from index direction"
                )

        # --------------------------------------------------------------
        # Status
        # --------------------------------------------------------------

        first_status = analyzed[0].status
        status = first_status

        # --------------------------------------------------------------
        # Timestamp
        # --------------------------------------------------------------

        resolved_timestamp = (
            timestamp
            or strongest.timestamp
        )

        # --------------------------------------------------------------
        # Final snapshot
        # --------------------------------------------------------------

        return MarketSnapshot(
            indices=analyzed,
            breadth=breadth,
            regime=regime,
            score=total_score,
            strongest_index=strongest.symbol,
            weakest_index=weakest.symbol,
            status=status,
            timestamp=resolved_timestamp,
            reasons=reasons,
        )
