"""
Base interface for all market data providers.
"""

from abc import ABC, abstractmethod

from batip.models import (
    ExpiryInfo,
    FutureQuote,
    MarketStatus,
    SpotQuote,
    VixQuote,
)


class MarketDataProvider(ABC):
    """Abstract interface implemented by all market data providers."""

    @abstractmethod
    def get_spot(self) -> SpotQuote:
        pass

    @abstractmethod
    def get_future(self) -> FutureQuote:
        pass

    @abstractmethod
    def get_vix(self) -> VixQuote:
        pass

    @abstractmethod
    def get_market_status(self) -> MarketStatus:
        pass

    @abstractmethod
    def get_expiry(self) -> ExpiryInfo:
        pass