"""
BATIP Option Chain Domain Models
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class OptionLeg:
    """
    Represents one option contract (either CE or PE).
    """

    strike: float

    option_type: str

    last_price: float

    bid_price: float

    ask_price: float

    volume: int

    open_interest: int

    change_in_oi: int

    implied_volatility: float


@dataclass(slots=True)
class OptionStrike:
    """
    Represents one strike containing both CE and PE.
    """

    strike: float

    call: OptionLeg

    put: OptionLeg


@dataclass(slots=True)
class OptionChain:
    """
    Complete option chain.
    """

    symbol: str

    expiry: str

    spot_price: float

    timestamp: datetime

    strikes: list[OptionStrike] = field(default_factory=list)