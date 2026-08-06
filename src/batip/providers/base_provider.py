from __future__ import annotations

from abc import ABC, abstractmethod

from batip.models import OptionChain


class MarketDataProvider(ABC):
    """Base class for all market data providers."""

    @abstractmethod
    def get_option_chain(
        self,
        symbol: str = "BANKNIFTY",
    ) -> OptionChain:
        """Return an option chain."""
        raise NotImplementedError