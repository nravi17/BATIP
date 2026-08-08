"""
BATIP Dashboard Service

Builds a unified dashboard snapshot using the existing
BATIP analytics and SignalEngine.

The SignalEngine remains the single source of truth
for the final market signal.
"""

from dataclasses import dataclass

from batip.analytics.max_pain import MaxPainCalculator
from batip.analytics.oi_analysis import OIAnalyzer, OIType
from batip.analytics.pcr import PCRCalculator
from batip.analytics.signal_engine import SignalEngine
from batip.analytics.support_resistance import (
    SupportResistanceCalculator,
)
from batip.providers.nse_provider import NSEProvider


@dataclass(slots=True)
class DashboardSnapshot:
    """Complete dashboard-ready market snapshot."""

    # --------------------------------------------------
    # Market
    # --------------------------------------------------

    symbol: str
    spot: float
    expiry: str
    atm: float

    # --------------------------------------------------
    # Option sentiment
    # --------------------------------------------------

    pcr: float
    pcr_signal: str

    # --------------------------------------------------
    # Max pain
    # --------------------------------------------------

    max_pain: float
    max_pain_distance: float

    # --------------------------------------------------
    # Support / resistance
    # --------------------------------------------------

    support: float
    strong_support: float
    resistance: float
    strong_resistance: float

    # --------------------------------------------------
    # OI walls
    # --------------------------------------------------

    put_oi_wall: float
    call_oi_wall: float
    max_put_delta_oi: float
    max_call_delta_oi: float

    # --------------------------------------------------
    # OI analysis
    # --------------------------------------------------

    bullish_oi: int
    bearish_oi: int
    neutral_oi: int

    # --------------------------------------------------
    # Signal scores
    #
    # These are dashboard display values derived from
    # the SignalEngine's final net score.
    # --------------------------------------------------

    bullish_score: int
    bearish_score: int

    # --------------------------------------------------
    # Existing SignalEngine result
    # --------------------------------------------------

    signal: str
    direction: str
    strength: str
    score: int
    confidence: float
    reasons: list[str]


class DashboardService:
    """
    Build a dashboard snapshot from live NSE data.

    No independent trading logic is implemented here.
    The existing SignalEngine determines the final signal.
    """

    def __init__(self) -> None:
        self.provider = NSEProvider()

    def get_snapshot(
        self,
        symbol: str = "BANKNIFTY",
    ) -> DashboardSnapshot:

        # --------------------------------------------------
        # 1. Fetch live option chain
        # --------------------------------------------------

        chain = self.provider.get_option_chain(symbol)

        # --------------------------------------------------
        # 2. Existing analytics
        # --------------------------------------------------

        pcr_result = PCRCalculator(chain).calculate()

        max_pain_result = MaxPainCalculator(chain).calculate()

        oi_analysis = OIAnalyzer(chain).analyze()

        sr_result = SupportResistanceCalculator(
            chain
        ).calculate()

        # --------------------------------------------------
        # 3. ATM strike
        # --------------------------------------------------

        atm_strike = min(
            chain.strikes,
            key=lambda strike: abs(
                strike.strike - chain.spot_price
            ),
        ).strike

        # --------------------------------------------------
        # 4. OI sentiment counts
        # --------------------------------------------------

        bullish_oi = sum(
            1
            for item in oi_analysis
            if item.signal in (
                OIType.LONG_BUILDUP,
                OIType.SHORT_COVERING,
            )
        )

        bearish_oi = sum(
            1
            for item in oi_analysis
            if item.signal in (
                OIType.SHORT_BUILDUP,
                OIType.LONG_UNWINDING,
            )
        )

        neutral_oi = sum(
            1
            for item in oi_analysis
            if item.signal == OIType.NEUTRAL
        )

        # --------------------------------------------------
        # 5. OI walls
        # --------------------------------------------------

        put_oi_wall = max(
            chain.strikes,
            key=lambda strike: strike.put.open_interest,
        )

        call_oi_wall = max(
            chain.strikes,
            key=lambda strike: strike.call.open_interest,
        )

        max_put_delta_oi = max(
            chain.strikes,
            key=lambda strike: strike.put.change_in_oi,
        )

        max_call_delta_oi = max(
            chain.strikes,
            key=lambda strike: strike.call.change_in_oi,
        )

        # --------------------------------------------------
        # 6. Strong support / resistance
        #
        # Existing calculator provides primary S/R.
        # Strong levels are derived from the next strongest
        # OI level on the relevant side.
        # --------------------------------------------------

        below_spot = [
            strike
            for strike in chain.strikes
            if strike.strike < chain.spot_price
        ]

        above_spot = [
            strike
            for strike in chain.strikes
            if strike.strike > chain.spot_price
        ]

        below_sorted = sorted(
            below_spot,
            key=lambda strike: strike.put.open_interest,
            reverse=True,
        )

        above_sorted = sorted(
            above_spot,
            key=lambda strike: strike.call.open_interest,
            reverse=True,
        )

        strong_support = (
            below_sorted[1].strike
            if len(below_sorted) > 1
            else sr_result.support
        )

        strong_resistance = (
            above_sorted[1].strike
            if len(above_sorted) > 1
            else sr_result.resistance
        )

        # --------------------------------------------------
        # 7. EXISTING SIGNAL ENGINE
        #
        # Dashboard does NOT create a separate market
        # signal. SignalEngine remains the source of truth.
        # --------------------------------------------------

        signal_result = SignalEngine(
            chain=chain,
            pcr=pcr_result.value,
            max_pain=max_pain_result,
            support_resistance=sr_result,
        ).calculate()

        # --------------------------------------------------
        # 8. Dashboard score
        #
        # Convert the existing net SignalEngine score into
        # two display-friendly values.
        #
        # Example:
        #   score = +5  -> bullish_score=5, bearish_score=0
        #   score = -4  -> bullish_score=0, bearish_score=4
        #   score =  0  -> both are 0
        # --------------------------------------------------

        net_score = int(signal_result.score)

        bullish_score = max(net_score, 0)
        bearish_score = max(-net_score, 0)

        # --------------------------------------------------
        # 9. Final dashboard snapshot
        # --------------------------------------------------

        return DashboardSnapshot(
            # Market
            symbol=chain.symbol,
            spot=chain.spot_price,
            expiry=chain.expiry,
            atm=atm_strike,

            # PCR
            pcr=pcr_result.value,
            pcr_signal=str(pcr_result.signal),

            # Max pain
            max_pain=max_pain_result.strike,
            max_pain_distance=(
                max_pain_result.strike
                - chain.spot_price
            ),

            # Support / resistance
            support=sr_result.support,
            strong_support=strong_support,
            resistance=sr_result.resistance,
            strong_resistance=strong_resistance,

            # OI walls
            put_oi_wall=put_oi_wall.strike,
            call_oi_wall=call_oi_wall.strike,
            max_put_delta_oi=max_put_delta_oi.strike,
            max_call_delta_oi=max_call_delta_oi.strike,

            # OI analysis
            bullish_oi=bullish_oi,
            bearish_oi=bearish_oi,
            neutral_oi=neutral_oi,

            # Signal scores
            bullish_score=bullish_score,
            bearish_score=bearish_score,

            # SignalEngine
            signal=str(signal_result.signal),
            direction=signal_result.direction,
            strength=str(signal_result.strength),
            score=signal_result.score,
            confidence=signal_result.confidence,
            reasons=signal_result.reasons,
        )