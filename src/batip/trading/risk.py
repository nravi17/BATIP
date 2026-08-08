"""
BATIP Risk Engine.

Calculates paper-trading position size and validates trade risk.

No broker connectivity and no order execution.
"""


class RiskEngine:
    """Calculate and validate trade risk."""

    @staticmethod
    def risk_amount(
        capital: float,
        risk_percent: float,
    ) -> float:
        """Calculate maximum monetary risk."""

        if capital <= 0:
            return 0.0

        if risk_percent <= 0:
            return 0.0

        return capital * risk_percent / 100.0

    @staticmethod
    def risk_per_share(
        entry: float,
        stop_loss: float,
    ) -> float:
        """Calculate absolute risk per share."""

        if entry <= 0 or stop_loss <= 0:
            return 0.0

        return abs(entry - stop_loss)

    @staticmethod
    def position_size(
        capital: float,
        risk_percent: float,
        entry: float,
        stop_loss: float,
    ) -> int:
        """Calculate maximum whole-share position size."""

        risk_amount = RiskEngine.risk_amount(
            capital,
            risk_percent,
        )

        risk_per_share = RiskEngine.risk_per_share(
            entry,
            stop_loss,
        )

        if risk_amount <= 0 or risk_per_share <= 0:
            return 0

        return int(risk_amount / risk_per_share)

    @staticmethod
    def maximum_loss(
        position_size: int,
        entry: float,
        stop_loss: float,
    ) -> float:
        """Calculate maximum loss at stop loss."""

        if position_size <= 0:
            return 0.0

        risk_per_share = RiskEngine.risk_per_share(
            entry,
            stop_loss,
        )

        return position_size * risk_per_share

    @staticmethod
    def risk_reward(
        entry: float,
        stop_loss: float,
        target: float,
    ) -> float:
        """Calculate risk/reward ratio."""

        risk = RiskEngine.risk_per_share(
            entry,
            stop_loss,
        )

        if risk <= 0:
            return 0.0

        reward = abs(target - entry)

        return reward / risk

    @staticmethod
    def validate_direction(
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
    ) -> tuple[bool, str]:
        """Validate price placement for long/short trades."""

        direction = direction.strip().lower()

        if direction in {"bullish", "long", "buy"}:
            if stop_loss >= entry:
                return False, "Long stop loss must be below entry"

            if target_1 <= entry:
                return False, "Long target 1 must be above entry"

            if target_2 <= target_1:
                return False, "Long target 2 must be above target 1"

            return True, "Long trade structure is valid"

        if direction in {"bearish", "short", "sell"}:
            if stop_loss <= entry:
                return False, "Short stop loss must be above entry"

            if target_1 >= entry:
                return False, "Short target 1 must be below entry"

            if target_2 >= target_1:
                return False, "Short target 2 must be below target 1"

            return True, "Short trade structure is valid"

        return False, "Unknown trade direction"

    @staticmethod
    def validate_risk_reward(
        entry: float,
        stop_loss: float,
        target_1: float,
        minimum_ratio: float = 1.5,
    ) -> tuple[bool, str]:
        """Validate minimum risk/reward for target 1."""

        if minimum_ratio <= 0:
            return False, "Minimum risk/reward must be positive"

        ratio = RiskEngine.risk_reward(
            entry,
            stop_loss,
            target_1,
        )

        if ratio < minimum_ratio:
            return (
                False,
                f"Risk/reward {ratio:.2f} is below "
                f"minimum {minimum_ratio:.2f}",
            )

        return True, f"Risk/reward {ratio:.2f} is acceptable"