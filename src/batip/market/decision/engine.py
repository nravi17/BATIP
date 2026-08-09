"""
BATIP Market Decision Engine.

Combines market-level intelligence signals into
a deterministic overall market action.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDecisionSnapshot:
    """Final market decision snapshot."""

    market_bias: str
    market_regime: str

    breadth_score: int
    sector_score: int
    stock_score: int

    decision_score: int
    direction: str
    action: str

    confidence: float


class MarketDecisionEngine:
    """Convert market intelligence into an actionable decision."""

    @staticmethod
    def direction_from_bias(market_bias: str) -> str:
        """Normalize market bias into a direction."""

        bias = str(market_bias).strip().lower()

        if bias == "bullish":
            return "Bullish"

        if bias == "bearish":
            return "Bearish"

        return "Neutral"

    @staticmethod
    def action_from_score(
        decision_score: int,
        confidence: float,
    ) -> str:
        """
        Convert decision score and confidence into an action.

        Strong positive score + sufficient confidence -> BUY
        Strong negative score + sufficient confidence -> SELL
        Otherwise -> WATCH
        """

        if confidence < 70:
            return "WATCH"

        if decision_score > 0:
            return "BUY"

        if decision_score < 0:
            return "SELL"

        return "WATCH"

    def analyze(
        self,
        market_bias: str,
        market_regime: str,
        breadth_score: int,
        sector_score: int,
        stock_score: int,
        confidence: float,
    ) -> MarketDecisionSnapshot:
        """Generate a deterministic market decision."""

        decision_score = (
            breadth_score
            + sector_score
            + stock_score
        )

        direction = self.direction_from_bias(market_bias)

        action = self.action_from_score(
            decision_score,
            confidence,
        )

        return MarketDecisionSnapshot(
            market_bias=market_bias,
            market_regime=market_regime,
            breadth_score=breadth_score,
            sector_score=sector_score,
            stock_score=stock_score,
            decision_score=decision_score,
            direction=direction,
            action=action,
            confidence=float(confidence),
        )