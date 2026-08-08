"""
Market Service
"""

from __future__ import annotations

from datetime import datetime

from batip.analytics.market_bias import MarketBiasEngine
from batip.analytics.max_pain import MaxPainCalculator
from batip.analytics.pcr import PCRCalculator
from batip.analytics.signal_engine import SignalEngine
from batip.analytics.support_resistance import (
    SupportResistanceCalculator,
)
from batip.providers.base_provider import MarketDataProvider
from batip.viewmodels import DashboardViewModel


class MarketService:
    """
    Builds all dashboard data from a market provider.
    """

    def __init__(
        self,
        provider: MarketDataProvider,
    ) -> None:
        self.provider = provider

    def get_dashboard_data(
        self,
        symbol: str = "BANKNIFTY",
    ) -> dict:
        """
        Fetch market data and calculate dashboard analytics.
        """

        chain = self.provider.get_option_chain(
            symbol=symbol
        )

        # ---------------------------------------------
        # Core analytics
        # ---------------------------------------------

        pcr_result = PCRCalculator(
            chain
        ).calculate()

        max_pain_result = MaxPainCalculator(
            chain
        ).calculate()

        support_result = SupportResistanceCalculator(
            chain
        ).calculate()

        # ---------------------------------------------
        # Market bias
        # ---------------------------------------------

        market_bias_result = MarketBiasEngine(
            chain,
            pcr=pcr_result.value,
        ).calculate()

        # ---------------------------------------------
        # Final trading signal
        # ---------------------------------------------

        signal_result = SignalEngine(
            chain=chain,
            pcr=pcr_result.value,
            max_pain=max_pain_result,
            support_resistance=support_result,
        ).calculate()

        return {
            "chain": chain,
            "pcr": pcr_result,
            "max_pain": max_pain_result,
            "support": support_result,
            "market_bias": market_bias_result,
            "signal": signal_result,
        }

    def get_dashboard_view(
        self,
        symbol: str = "BANKNIFTY",
    ) -> DashboardViewModel:
        """
        Return display-ready dashboard data.
        """

        data = self.get_dashboard_data(
            symbol=symbol
        )

        chain = data["chain"]

        return DashboardViewModel(
            symbol=chain.symbol,
            expiry=chain.expiry,
            spot=f"{chain.spot_price:,.2f}",
            pcr=f"{data['pcr'].value:.2f}",
            max_pain=str(
                data["max_pain"].strike
            ),
            support=str(
                data["support"].support
            ),
            resistance=str(
                data["support"].resistance
            ),
            updated=datetime.now().strftime(
                "%d-%b-%Y %H:%M:%S"
            ),
        )