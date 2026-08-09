"""
BATIP Trade Decision Engine.

Combines opportunity intelligence and trade setup generation
into a single paper-trading decision.

No broker connectivity and no order execution.
"""

from dataclasses import dataclass

from batip.market.opportunity import OpportunityEngine
from batip.trading.models import TradeSetup
from batip.trading.setup import TradeSetupEngine


@dataclass(slots=True)
class TradeDecision:
    """Final BATIP paper-trading decision."""

    symbol: str

    opportunity_score: int
    recommendation: str
    direction: str
    confidence: float

    intraday: str
    overnight: str

    trade_action: str

    setup: TradeSetup | None

    reasons: list[str]


class TradeDecisionEngine:
    """Convert market intelligence into a paper-trading decision."""

    def __init__(
        self,
        *,
        capital: float = 100000.0,
        risk_percent: float = 1.0,
        minimum_risk_reward: float = 1.5,
    ) -> None:

        self.opportunity_engine = OpportunityEngine()

        self.setup_engine = TradeSetupEngine(
            capital=capital,
            risk_percent=risk_percent,
            minimum_risk_reward=minimum_risk_reward,
        )

    @staticmethod
    def _direction_from_levels(
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
    ) -> str | None:
        """
        Determine trade direction from explicit price levels.

        Long:
            stop_loss < entry < target_1 < target_2

        Short:
            stop_loss > entry > target_1 > target_2

        Returns None when the levels do not clearly describe
        either a long or short setup.
        """

        if (
            stop_loss < entry
            and target_1 > entry
            and target_2 > target_1
        ):
            return "Bullish"

        if (
            stop_loss > entry
            and target_1 < entry
            and target_2 < target_1
        ):
            return "Bearish"

        return None

    def evaluate(
        self,
        *,
        symbol: str,
        stock_score: int,
        technical_score: int,
        market_score: int,
        sector_score: int,
        entry: float | None = None,
        stop_loss: float | None = None,
        target_1: float | None = None,
        target_2: float | None = None,
    ) -> TradeDecision:
        """Build a complete paper-trading decision."""

        opportunity = self.opportunity_engine.evaluate(
            stock_score=stock_score,
            technical_score=technical_score,
            market_score=market_score,
            sector_score=sector_score,
        )

        recommendation = opportunity.recommendation

        setup = None
        reasons = list(opportunity.reasons)

        prices_available = all(
            value is not None
            for value in (
                entry,
                stop_loss,
                target_1,
                target_2,
            )
        )

        # ---------------------------------------------------------
        # Determine direction.
        #
        # If explicit trade levels are supplied and clearly define
        # a long/short structure, use the price structure.
        #
        # Otherwise use the opportunity engine direction.
        # ---------------------------------------------------------

        direction = opportunity.direction

        if prices_available:
            level_direction = self._direction_from_levels(
                float(entry),
                float(stop_loss),
                float(target_1),
                float(target_2),
            )

            if level_direction is not None:
                direction = level_direction

        # ---------------------------------------------------------
        # Build setup.
        # ---------------------------------------------------------

        if prices_available:
            setup = self.setup_engine.build(
                symbol=symbol,
                direction=direction,
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                intraday=opportunity.intraday,
                overnight=opportunity.overnight,
                confidence=opportunity.confidence,
            )

            if not setup.valid:
                reasons.append(setup.reason)

        # ---------------------------------------------------------
        # Determine trade action.
        #
        # IMPORTANT:
        # Score 70 is WATCH.
        #
        # Only a genuine strong recommendation with a valid setup
        # is authorized for paper trading.
        # ---------------------------------------------------------

        if opportunity.opportunity_score == 70:
            trade_action = "WATCH"

        elif setup is not None and not setup.valid:
            trade_action = "AVOID"

        elif recommendation in {
            "STRONG BUY",
            "STRONG SELL",
        }:
            if setup is not None and setup.valid:
                trade_action = "TRADE"
            else:
                trade_action = "WATCH"

        elif recommendation in {
            "BUY",
            "SELL",
            "WATCH",
        }:
            trade_action = "WATCH"

        else:
            trade_action = "AVOID"

        # ---------------------------------------------------------
        # Missing levels.
        # ---------------------------------------------------------

        if (
            setup is None
            and recommendation in {
                "STRONG BUY",
                "STRONG SELL",
            }
        ):
            reasons.append(
                "Trade levels are required before a paper trade "
                "can be created"
            )

        return TradeDecision(
            symbol=symbol,
            opportunity_score=opportunity.opportunity_score,
            recommendation=recommendation,
            direction=direction,
            confidence=opportunity.confidence,
            intraday=opportunity.intraday,
            overnight=opportunity.overnight,
            trade_action=trade_action,
            setup=setup,
            reasons=reasons,
        )