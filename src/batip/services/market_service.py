"""
Market Service
"""

from batip.analytics.max_pain import MaxPainCalculator
from batip.analytics.pcr import PCRCalculator
from batip.analytics.support_resistance import SupportResistanceCalculator
from batip.providers.base_provider import MarketDataProvider


class MarketService:

    def __init__(self, provider: MarketDataProvider):
        self.provider = provider

    def get_dashboard_data(self):

        chain = self.provider.get_option_chain()

        return {
            "chain": chain,
            "pcr": PCRCalculator(chain).calculate(),
            "max_pain": MaxPainCalculator(chain).calculate(),
            "support": SupportResistanceCalculator(chain).calculate(),
        }