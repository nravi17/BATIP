from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class SpotQuote:
    symbol: str
    price: float
    change: float
    change_percent: float
    timestamp: datetime


@dataclass(slots=True)
class FutureQuote:
    symbol: str
    expiry: str
    price: float
    change: float
    change_percent: float
    open_interest: Optional[int]
    timestamp: datetime


@dataclass(slots=True)
class VixQuote:
    value: float
    change: float
    change_percent: float
    timestamp: datetime


@dataclass(slots=True)
class MarketStatus:
    is_open: bool
    message: str
    timestamp: datetime


@dataclass(slots=True)
class ExpiryInfo:
    current_week: str
    next_week: str
    monthly: str