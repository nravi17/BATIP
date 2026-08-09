"""
BATIP Index Scanner.

Evaluates normalized index snapshots and determines:

- directional score
- strongest index
- weakest index
- overall market regime

This module does not place trades.
"""

from __future__ import annotations

from batip.market.models import (
    IndexSnapshot,
    MarketDirection,
    MarketRegime,
    MarketSnapshot,
)


class IndexScanner:
    """Analyze a collection of index snapshots."""

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

    @staticmethod
    def direction_from_score(score: int) -> MarketDirection:
        """Convert score into a market direction."""

        if score > 0:
            return MarketDirection.BULLISH

        if score < 0:
            return MarketDirection.BEARISH

        return MarketDirection.NEUTRAL

    @staticmethod
    def regime_from_score(score: int) -> MarketRegime:
        """
        Convert aggregate score into market regime.

        Index-only scoring:
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

    def scan(
        self,
        indices: list[IndexSnapshot] | None = None,
    ) -> MarketSnapshot:
        """
        Analyze all supplied indices.

        None entries are ignored.

        An empty or missing index collection returns an unavailable,
        neutral MarketSnapshot.
        """

        if not indices:
            return MarketSnapshot()

        # Ignore invalid None entries.
        valid_indices = [
            index
            for index in indices
            if index is not None
        ]

        if not valid_indices:
            return MarketSnapshot()

        analyzed: list[IndexSnapshot] = []

        for index in valid_indices:
            score = self.score_index(index)

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
                    direction=self.direction_from_score(score),
                    score=score,
                    status=index.status,
                    timestamp=index.timestamp,
                    metadata=dict(index.metadata),
                )
            )

        total_score = sum(
            self.score_index(index)
            for index in valid_indices
        )

        strongest = max(
            analyzed,
            key=lambda index: index.change_percent,
        )

        weakest = min(
            analyzed,
            key=lambda index: index.change_percent,
        )

        regime = self.regime_from_score(total_score)

        reasons: list[str] = []

        if total_score > 0:
            reasons.append(
                "Major indices show positive breadth of movement."
            )
        elif total_score < 0:
            reasons.append(
                "Major indices show negative breadth of movement."
            )
        else:
            reasons.append(
                "Major indices are mixed or unchanged."
            )

        reasons.append(
            f"Strongest index: {strongest.symbol} "
            f"({strongest.change_percent:+.2f}%)."
        )

        reasons.append(
            f"Weakest index: {weakest.symbol} "
            f"({weakest.change_percent:+.2f}%)."
        )

        return MarketSnapshot(
            indices=analyzed,
            regime=regime,
            score=total_score,
            strongest_index=strongest.symbol,
            weakest_index=weakest.symbol,
            status=(
                analyzed[0].status
                if all(
                    index.status == analyzed[0].status
                    for index in analyzed
                )
                else analyzed[0].status
            ),
            timestamp=strongest.timestamp,
            reasons=reasons,
        )