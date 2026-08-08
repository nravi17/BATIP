"""
BATIP Trade Models.

Paper-trading models only.
No broker connectivity or order execution.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class TradeSetup:
    """Normalized trade setup."""

    symbol: str
    direction: str

    entry: float
    stop_loss: float
    target_1: float
    target_2: float

    risk_per_share: float = 0.0
    reward_1_per_share: float = 0.0
    reward_2_per_share: float = 0.0

    risk_reward_1: float = 0.0
    risk_reward_2: float = 0.0

    capital: float = 0.0
    risk_percent: float = 1.0

    risk_amount: float = 0.0
    position_size: int = 0
    maximum_loss: float = 0.0

    intraday: str = "AVOID"
    overnight: str = "AVOID"

    confidence: float = 0.0
    invalidation: str = ""

    valid: bool = True
    reason: str = ""