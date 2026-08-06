"""
Market Service
"""
from datetime import datetime

from batip.analytics.max_pain import MaxPainCalculator
from batip.analytics.pcr import PCRCalculator
from batip.analytics.support_resistance import (
    SupportResistanceCalculator,
)
from batip.providers.base_provider import MarketDataProvider
from batip.viewmodels import DashboardViewModel


class MarketService:
    """Builds all dashboard data from a market provider."""

    def __init__(
        self,
        provider: MarketDataProvider,
    ) -> None:
        self.provider = provider

    def get_dashboard_data(self) -> dict:
        """Return all dashboard data."""
        chain = self.provider.get_option_chain()
        return {
            "chain": chain,
            "pcr": PCRCalculator(chain).calculate(),
            "max_pain": MaxPainCalculator(chain).calculate(),
            "support": SupportResistanceCalculator(chain).calculate(),
        }

    def get_dashboard_view(self) -> DashboardViewModel:
        """Return display-ready dashboard data."""
        data = self.get_dashboard_data()
        chain = data["chain"]
        return DashboardViewModel(
            symbol=chain.symbol,
            expiry=chain.expiry,
            spot=f"{chain.spot_price:,.2f}",
            pcr=f"{data['pcr'].value:.2f}",
            max_pain=str(data["max_pain"].strike),
            support=str(data["support"].support),
            resistance=str(data["support"].resistance),
            updated=datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        )