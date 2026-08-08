"""
BATIP Trade Setup Generator.

Converts an opportunity assessment into a paper-trading setup.

No broker connectivity and no order execution.
"""

from batip.trading.models import TradeSetup
from batip.trading.risk import RiskEngine


class TradeSetupEngine:
    """Generate risk-controlled trade setups."""

    def __init__(
        self,
        capital: float = 100000.0,
        risk_percent: float = 1.0,
        minimum_risk_reward: float = 1.5,
    ) -> None:
        self.capital = capital
        self.risk_percent = risk_percent
        self.minimum_risk_reward = minimum_risk_reward

    def build(
        self,
        *,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        intraday: str = "AVOID",
        overnight: str = "AVOID",
        confidence: float = 0.0,
    ) -> TradeSetup:
        """Build and validate a complete trade setup."""

        # ---------------------------------------------------------
        # 1. Validate trade direction and price structure
        # ---------------------------------------------------------
        valid_direction, direction_reason = (
            RiskEngine.validate_direction(
                direction,
                entry,
                stop_loss,
                target_1,
                target_2,
            )
        )

        # ---------------------------------------------------------
        # 2. Calculate monetary risk
        # ---------------------------------------------------------
        risk_amount = RiskEngine.risk_amount(
            self.capital,
            self.risk_percent,
        )

        # ---------------------------------------------------------
        # 3. Calculate risk/reward metrics
        # ---------------------------------------------------------
        risk_per_share = RiskEngine.risk_per_share(
            entry,
            stop_loss,
        )

        reward_1 = abs(target_1 - entry)
        reward_2 = abs(target_2 - entry)

        rr_1 = RiskEngine.risk_reward(
            entry,
            stop_loss,
            target_1,
        )

        rr_2 = RiskEngine.risk_reward(
            entry,
            stop_loss,
            target_2,
        )

        # ---------------------------------------------------------
        # 4. Validate minimum risk/reward
        # ---------------------------------------------------------
        valid_rr, rr_reason = (
            RiskEngine.validate_risk_reward(
                entry,
                stop_loss,
                target_1,
                self.minimum_risk_reward,
            )
        )

        # ---------------------------------------------------------
        # 5. Calculate position size
        #
        # BATIP setup sizing intentionally uses a 10x sizing
        # divisor relative to the raw RiskEngine calculation.
        #
        # Example:
        # Capital       = 100,000
        # Risk          = 1% = 1,000
        # Risk/share    = 5
        # Raw size      = 200
        # BATIP size    = 20
        # ---------------------------------------------------------
        raw_position_size = RiskEngine.position_size(
            self.capital,
            self.risk_percent,
            entry,
            stop_loss,
        )

        position_size = raw_position_size // 10

        # ---------------------------------------------------------
        # 6. Maximum loss based on BATIP position size
        # ---------------------------------------------------------
        maximum_loss = RiskEngine.maximum_loss(
            position_size,
            entry,
            stop_loss,
        )

        # ---------------------------------------------------------
        # 7. Overall validity
        # ---------------------------------------------------------
        valid = (
            valid_direction
            and valid_rr
            and position_size > 0
        )

        # ---------------------------------------------------------
        # 8. Reason
        # ---------------------------------------------------------
        if valid:
            reason = "Trade setup is valid"

        elif not valid_direction:
            reason = direction_reason

        elif not valid_rr:
            reason = rr_reason

        else:
            reason = "Position size is zero"

        # ---------------------------------------------------------
        # 9. Invalidation level
        # ---------------------------------------------------------
        normalized_direction = direction.strip().lower()

        if normalized_direction in {
            "bullish",
            "long",
            "buy",
        }:
            invalidation = f"Below {stop_loss:g}"

        elif normalized_direction in {
            "bearish",
            "short",
            "sell",
        }:
            invalidation = f"Above {stop_loss:g}"

        else:
            invalidation = ""

        # ---------------------------------------------------------
        # 10. Clamp confidence to 0–100
        # ---------------------------------------------------------
        confidence = min(
            max(confidence, 0.0),
            100.0,
        )

        # ---------------------------------------------------------
        # 11. Build final TradeSetup
        # ---------------------------------------------------------
        return TradeSetup(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            risk_per_share=risk_per_share,
            reward_1_per_share=reward_1,
            reward_2_per_share=reward_2,
            risk_reward_1=rr_1,
            risk_reward_2=rr_2,
            capital=self.capital,
            risk_percent=self.risk_percent,
            risk_amount=risk_amount,
            position_size=position_size,
            maximum_loss=maximum_loss,
            intraday=intraday,
            overnight=overnight,
            confidence=confidence,
            invalidation=invalidation,
            valid=valid,
            reason=reason,
        )