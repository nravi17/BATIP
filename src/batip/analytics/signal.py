"""
BATIP Signal Engine Models

Defines the deterministic trading-signal result used
by the BATIP analytics and dashboard layers.
"""

from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    WAIT = "Wait"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"


class SignalStrength(str, Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    WEAK = "Weak"


@dataclass(slots=True)
class SignalResult:
    signal: Signal
    strength: SignalStrength
    score: int
    confidence: float
    direction: str
    reasons: list[str]