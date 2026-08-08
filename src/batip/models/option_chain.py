"""
BATIP Option Chain Domain Models
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class OptionLeg:
    """Represents one option contract."""

    strike: float
    option_type: str

    last_price: float
    bid_price: float
    ask_price: float

    volume: int
    open_interest: int
    change_in_oi: int
    implied_volatility: float

    # New market-price fields.
    # Defaults keep existing tests/mock data compatible.
    previous_close: float = 0.0
    price_change: float = 0.0
    price_change_percent: float = 0.0

    expiry: str | None = None
    contract_symbol: str | None = None


@dataclass(slots=True)
class OptionStrike:
    """Represents one strike containing CE and PE."""

    strike: float
    call: OptionLeg
    put: OptionLeg


@dataclass(slots=True)
class OptionChain:
    """Complete option chain."""

    symbol: str
    expiry: str
    spot_price: float
    timestamp: datetime
    source: str = "unknown"
    data_status: str = "UNKNOWN"
    strikes: list[OptionStrike] = field(
        default_factory=list
    )