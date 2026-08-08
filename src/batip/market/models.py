"""
BATIP Market Intelligence Models.

Normalized models used by the market/index intelligence layer.
These models are deliberately independent of NSE response formats.
"""

from dataclasses import dataclass, field
from enum import Enum


class MarketDataStatus(str, Enum):
    """Availability/status of market data."""

    LIVE = "LIVE"
    STALE = "STALE"
    MOCK = "MOCK"
    UNAVAILABLE = "UNAVAILABLE"


class MarketDirection(str, Enum):
    """Directional interpretation of an index/market."""

    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class MarketRegime(str, Enum):
    """Overall market regime."""

    STRONG_BULLISH = "Strong Bullish"
    BULLISH = "Bullish"
    NEUTRAL = "Neutral"
    BEARISH = "Bearish"
    STRONG_BEARISH = "Strong Bearish"


@dataclass(slots=True)
class IndexSnapshot:
    """
    Normalized snapshot for a single market index.
    """

    symbol: str
    name: str
    value: float

    change: float = 0.0
    change_percent: float = 0.0

    previous_close: float | None = None
    day_open: float | None = None
    day_high: float | None = None
    day_low: float | None = None

    direction: MarketDirection = MarketDirection.NEUTRAL
    score: int = 0

    status: MarketDataStatus = MarketDataStatus.UNAVAILABLE

    timestamp: str | None = None

    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class MarketBreadth:
    """
    Market breadth statistics.
    """

    advances: int = 0
    declines: int = 0
    unchanged: int = 0

    advance_decline_ratio: float = 0.0
    breadth_score: float = 0.0

    direction: MarketDirection = MarketDirection.NEUTRAL

    status: MarketDataStatus = MarketDataStatus.UNAVAILABLE


@dataclass(slots=True)
class MarketSnapshot:
    """
    Unified market-level snapshot.

    Contains indices and breadth information but does not
    contain trading recommendations.
    """

    indices: list[IndexSnapshot] = field(default_factory=list)

    breadth: MarketBreadth | None = None

    regime: MarketRegime = MarketRegime.NEUTRAL
    score: int = 0

    strongest_index: str | None = None
    weakest_index: str | None = None

    status: MarketDataStatus = MarketDataStatus.UNAVAILABLE

    timestamp: str | None = None

    reasons: list[str] = field(default_factory=list)