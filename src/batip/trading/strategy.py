"""
BATIP Strategy / Signal Engine.

Converts market-analysis inputs into a normalized trading signal.

This module does not:
- execute orders
- manage positions
- calculate portfolio allocation
- connect to a broker

It only evaluates a trading setup and produces a signal.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TradingSignal:
    """Normalized trading signal produced by the strategy engine."""

    symbol: str
    direction: str
    signal: str
    score: float
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    risk_reward: float
    reason: str


class StrategyEngine:
    """
    Evaluate a trading setup using technical/market inputs.

    Signal levels:
        TRADE  -> setup is strong enough to trade
        WATCH  -> setup has potential but is not strong enough
        AVOID  -> setup should not be traded
    """

    TRADE_THRESHOLD = 70.0
    WATCH_THRESHOLD = 50.0

    @staticmethod
    def _normalize_direction(direction: str) -> str:
        """Normalize direction to LONG or SHORT."""

        if not isinstance(direction, str):
            return ""

        value = direction.strip().upper()

        if value in {"LONG", "BUY", "BULLISH"}:
            return "LONG"

        if value in {"SHORT", "SELL", "BEARISH"}:
            return "SHORT"

        return ""

    @staticmethod
    def calculate_risk_reward(
        entry: float,
        stop_loss: float,
        target: float,
    ) -> float:
        """Calculate risk/reward ratio."""

        if entry <= 0 or stop_loss <= 0 or target <= 0:
            return 0.0

        risk = abs(entry - stop_loss)

        if risk <= 0:
            return 0.0

        reward = abs(target - entry)

        return reward / risk

    @staticmethod
    def calculate_score(
        trend_score: float,
        momentum_score: float,
        volume_score: float,
        risk_reward: float,
    ) -> float:
        """
        Calculate strategy score.

        Weighted components:
            Trend    : 35%
            Momentum : 25%
            Volume   : 20%
            R/R      : 20%

        Each component is normalized to 0-100.
        """

        trend = max(0.0, min(100.0, float(trend_score)))
        momentum = max(0.0, min(100.0, float(momentum_score)))
        volume = max(0.0, min(100.0, float(volume_score)))

        # Convert risk/reward into a 0-100 score.
        rr_score = min(100.0, max(0.0, float(risk_reward) / 3.0 * 100.0))

        score = (
            trend * 0.35
            + momentum * 0.25
            + volume * 0.20
            + rr_score * 0.20
        )

        return round(score, 2)

    @staticmethod
    def classify_signal(score: float) -> str:
        """Classify score as TRADE, WATCH, or AVOID."""

        # 70 is intentionally WATCH.
        # TRADE requires a score strictly above 70.
        if score > StrategyEngine.TRADE_THRESHOLD:
            return "TRADE"

        if score >= StrategyEngine.WATCH_THRESHOLD:
            return "WATCH"

        return "AVOID"

    @staticmethod
    def validate_setup(
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
    ) -> tuple[bool, str]:
        """Validate price structure for a long or short setup."""

        normalized = StrategyEngine._normalize_direction(direction)

        if not normalized:
            return False, "Unknown trading direction"

        if entry <= 0:
            return False, "Entry price must be positive"

        if stop_loss <= 0:
            return False, "Stop loss must be positive"

        if target_1 <= 0:
            return False, "Target 1 must be positive"

        if target_2 <= 0:
            return False, "Target 2 must be positive"

        if normalized == "LONG":
            if stop_loss >= entry:
                return False, "Long stop loss must be below entry"

            if target_1 <= entry:
                return False, "Long target 1 must be above entry"

            if target_2 <= target_1:
                return False, "Long target 2 must be above target 1"

        else:
            if stop_loss <= entry:
                return False, "Short stop loss must be above entry"

            if target_1 >= entry:
                return False, "Short target 1 must be below entry"

            if target_2 >= target_1:
                return False, "Short target 2 must be below target 1"

        return True, "Trading setup is valid"

    @classmethod
    def generate_signal(
        cls,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        trend_score: float,
        momentum_score: float,
        volume_score: float,
        minimum_risk_reward: float = 1.5,
    ) -> TradingSignal:
        """
        Generate a complete trading signal.

        The strategy first validates the setup, then calculates
        risk/reward and the final strategy score.
        """

        if not symbol or not symbol.strip():
            raise ValueError("Symbol is required")

        valid, reason = cls.validate_setup(
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
        )

        if not valid:
            raise ValueError(reason)

        if minimum_risk_reward <= 0:
            raise ValueError("Minimum risk/reward must be positive")

        normalized_direction = cls._normalize_direction(direction)

        risk_reward = cls.calculate_risk_reward(
            entry=entry,
            stop_loss=stop_loss,
            target=target_1,
        )

        score = cls.calculate_score(
            trend_score=trend_score,
            momentum_score=momentum_score,
            volume_score=volume_score,
            risk_reward=risk_reward,
        )

        signal = cls.classify_signal(score)

        if risk_reward < minimum_risk_reward:
            signal = "AVOID"
            reason = (
                f"Risk/reward {risk_reward:.2f} is below "
                f"minimum {minimum_risk_reward:.2f}"
            )
        elif signal == "TRADE":
            reason = (
                f"Strong {normalized_direction.lower()} setup; "
                f"strategy score {score:.2f}"
            )
        elif signal == "WATCH":
            reason = (
                f"Potential {normalized_direction.lower()} setup; "
                f"strategy score {score:.2f}"
            )
        else:
            reason = (
                f"Weak setup; strategy score {score:.2f}"
            )

        return TradingSignal(
            symbol=symbol.strip().upper(),
            direction=normalized_direction,
            signal=signal,
            score=score,
            entry=float(entry),
            stop_loss=float(stop_loss),
            target_1=float(target_1),
            target_2=float(target_2),
            risk_reward=round(risk_reward, 2),
            reason=reason,
        )

    @classmethod
    def evaluate(
        cls,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        trend_score: float,
        momentum_score: float,
        volume_score: float,
        minimum_risk_reward: float = 1.5,
    ) -> Optional[TradingSignal]:
        """
        Safe wrapper around generate_signal.

        Returns None instead of raising ValueError for an invalid setup.
        """

        try:
            return cls.generate_signal(
                symbol=symbol,
                direction=direction,
                entry=entry,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                trend_score=trend_score,
                momentum_score=momentum_score,
                volume_score=volume_score,
                minimum_risk_reward=minimum_risk_reward,
            )
        except ValueError:
            return None