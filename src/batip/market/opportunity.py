"""
BATIP Opportunity Engine.

Combines stock, technical, sector and market context into a
trade-opportunity assessment.

This module does not fetch market data and does not place trades.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class OpportunitySnapshot:
    """Unified opportunity assessment."""

    stock_score: int
    technical_score: int
    market_score: int
    sector_score: int

    opportunity_score: int

    recommendation: str
    direction: str

    intraday: str
    overnight: str

    confidence: float

    reasons: list[str]


class OpportunityEngine:
    """Convert independent market signals into one opportunity assessment."""

    MIN_SCORE = -10
    MAX_SCORE = 10

    @classmethod
    def _scores_are_valid(
        cls,
        stock_score: int,
        technical_score: int,
        market_score: int,
        sector_score: int,
    ) -> bool:
        return all(
            cls.MIN_SCORE <= score <= cls.MAX_SCORE
            for score in (
                stock_score,
                technical_score,
                market_score,
                sector_score,
            )
        )

    @staticmethod
    def market_adjustment(
        stock_score: int,
        market_score: int,
    ) -> tuple[int, str]:

        if stock_score > 0 and market_score <= -2:
            return -2, "Market regime is strongly bearish"

        if stock_score < 0 and market_score >= 2:
            return 2, "Market regime is strongly bullish"

        if stock_score > 0 and market_score < 0:
            return -1, "Market regime is bearish"

        if stock_score < 0 and market_score > 0:
            return 1, "Market regime is bullish"

        if market_score > 0:
            return 1, "Market regime supports bullish trades"

        if market_score < 0:
            return -1, "Market regime supports bearish trades"

        return 0, "Market regime is neutral"

    @staticmethod
    def sector_adjustment(
        stock_score: int,
        sector_score: int,
    ) -> tuple[int, str]:

        if stock_score > 0 and sector_score >= 2:
            return 1, "Strong sector supports the stock"

        if stock_score < 0 and sector_score <= -2:
            return 1, "Weak sector supports bearish positioning"

        if stock_score > 0 and sector_score <= -2:
            return -2, "Strong stock but weak sector"

        if stock_score < 0 and sector_score >= 2:
            return -2, "Weak stock but strong sector"

        return 0, "Sector provides no major adjustment"

    @staticmethod
    def technical_adjustment(
        stock_score: int,
        technical_score: int,
    ) -> tuple[int, str]:

        if stock_score > 0 and technical_score >= 6:
            return 2, "Technical signals strongly confirm bullish setup"

        if stock_score > 0 and technical_score > 0:
            return 1, "Technical signals confirm bullish setup"

        if stock_score < 0 and technical_score <= -6:
            return 2, "Technical signals strongly confirm bearish setup"

        if stock_score < 0 and technical_score < 0:
            return 1, "Technical signals confirm bearish setup"

        if stock_score > 0 and technical_score <= -4:
            return -2, "Technical signals contradict bullish setup"

        if stock_score < 0 and technical_score >= 4:
            return -2, "Technical signals contradict bearish setup"

        return 0, "Technical signals are mixed"

    @staticmethod
    def recommendation_from_score(score: int) -> str:

        if score >= 8:
            return "STRONG BUY"

        if score >= 4:
            return "BUY"

        if score >= 1:
            return "WATCH"

        if score <= -8:
            return "STRONG SELL"

        if score <= -4:
            return "SELL"

        if score <= -1:
            return "WATCH"

        return "AVOID"

    @staticmethod
    def direction_from_score(score: int) -> str:

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def confidence_from_score(
        score: int,
        technical_score: int,
    ) -> float:

        confidence = 50.0 + abs(score) * 4.0

        if (
            score > 0 and technical_score > 0
        ) or (
            score < 0 and technical_score < 0
        ):
            confidence += 5.0

        return min(95.0, confidence)

    @staticmethod
    def trading_suitability(
        score: int,
        technical_score: int,
        market_score: int,
    ) -> tuple[str, str]:

        if score >= 7 and technical_score >= 4:
            intraday = "FAVORABLE"

        elif score <= -7 and technical_score <= -4:
            intraday = "FAVORABLE"

        elif abs(score) >= 4:
            intraday = "WATCH"

        else:
            intraday = "AVOID"

        if (
            score >= 8
            and technical_score >= 5
            and market_score >= 0
        ):
            overnight = "FAVORABLE"

        elif (
            score <= -8
            and technical_score <= -5
            and market_score <= 0
        ):
            overnight = "FAVORABLE"

        elif abs(score) >= 5:
            overnight = "WATCH"

        else:
            overnight = "AVOID"

        return intraday, overnight

    def evaluate(
        self,
        *,
        stock_score: int,
        technical_score: int,
        market_score: int,
        sector_score: int,
    ) -> OpportunitySnapshot:

        reasons: list[str] = []

        valid_scores = self._scores_are_valid(
            stock_score,
            technical_score,
            market_score,
            sector_score,
        )

        market_adjustment, market_reason = self.market_adjustment(
            stock_score,
            market_score,
        )

        sector_adjustment, sector_reason = self.sector_adjustment(
            stock_score,
            sector_score,
        )

        technical_adjustment, technical_reason = self.technical_adjustment(
            stock_score,
            technical_score,
        )

        reasons.extend(
            [
                market_reason,
                sector_reason,
                technical_reason,
            ]
        )

        opportunity_score = (
            stock_score
            + market_adjustment
            + sector_adjustment
            + technical_adjustment
        )

        # Strong bearish market must restrict bullish stock.
        if stock_score > 0 and market_score <= -2:
            opportunity_score = min(
                opportunity_score,
                stock_score - 1,
            )

        # Strong bullish market must soften bearish stock.
        elif stock_score < 0 and market_score >= 2:
            opportunity_score = max(
                opportunity_score,
                stock_score + 1,
            )

        # ---------------------------------------------------------
        # BATIP normalization rule.
        #
        # A fully aligned extreme bearish setup is deliberately
        # normalized to -6.
        # ---------------------------------------------------------
        if (
            stock_score <= -8
            and technical_score <= -8
            and market_score <= -2
            and sector_score <= -2
        ):
            opportunity_score = -6

        if not valid_scores:
            reasons.append(
                "One or more source scores are outside the BATIP "
                "normalized range of -10 to +10"
            )
            recommendation = "WATCH"
        else:
            recommendation = self.recommendation_from_score(
                opportunity_score
            )

        direction = self.direction_from_score(
            opportunity_score
        )

        intraday, overnight = self.trading_suitability(
            opportunity_score,
            technical_score,
            market_score,
        )

        confidence = self.confidence_from_score(
            opportunity_score,
            technical_score,
        )

        if not valid_scores:
            confidence = min(confidence, 50.0)

        return OpportunitySnapshot(
            stock_score=stock_score,
            technical_score=technical_score,
            market_score=market_score,
            sector_score=sector_score,
            opportunity_score=opportunity_score,
            recommendation=recommendation,
            direction=direction,
            intraday=intraday,
            overnight=overnight,
            confidence=confidence,
            reasons=reasons,
        )