"""
BATIP Phase 2 Market Analyzer

Combines:
- PCR
- Max Pain
- Absolute OI
- Change in OI
- Price change
- OI walls
- Support / Resistance
- Market bias
- Trading action
"""

from dataclasses import dataclass

from batip.analytics.max_pain import MaxPainCalculator
from batip.analytics.oi_analysis import OIAnalyzer, OIType
from batip.analytics.pcr import PCRCalculator
from batip.models.option_chain import OptionChain


@dataclass(slots=True)
class MarketAnalysis:
    symbol: str
    spot: float
    expiry: str

    atm_strike: float

    pcr: float
    pcr_signal: str

    max_pain: float
    max_pain_distance: float

    support: float
    strong_support: float

    resistance: float
    strong_resistance: float

    put_oi_wall: float
    call_oi_wall: float

    put_change_oi_wall: float
    call_change_oi_wall: float

    bullish_oi: int
    bearish_oi: int
    neutral_oi: int

    bullish_score: int
    bearish_score: int

    bias: str
    confidence: float

    action: str
    entry: float
    stop_loss: float
    target_1: float
    target_2: float


class MarketAnalyzer:
    """
    BATIP Phase 2 market-analysis engine.

    Uses the ATM ± N strike region to avoid allowing
    distant illiquid strikes to dominate the analysis.
    """

    def __init__(
        self,
        chain: OptionChain,
        atm_range: int = 10,
    ) -> None:
        self.chain = chain
        self.atm_range = atm_range

    # ---------------------------------------------------------
    # Main analysis
    # ---------------------------------------------------------

    def analyze(self) -> MarketAnalysis:

        strikes = sorted(
            self.chain.strikes,
            key=lambda x: x.strike,
        )

        if not strikes:
            raise ValueError(
                "Option chain contains no strikes."
            )

        spot = float(self.chain.spot_price)

        # -----------------------------------------------------
        # ATM
        # -----------------------------------------------------

        atm = min(
            strikes,
            key=lambda x: abs(
                x.strike - spot
            ),
        )

        atm_strike = float(atm.strike)

        atm_index = strikes.index(atm)

        start = max(
            0,
            atm_index - self.atm_range,
        )

        end = min(
            len(strikes),
            atm_index + self.atm_range + 1,
        )

        relevant = strikes[start:end]

        # -----------------------------------------------------
        # PCR
        # -----------------------------------------------------

        pcr_result = PCRCalculator(
            self.chain
        ).calculate()

        pcr = float(pcr_result.value)

        # -----------------------------------------------------
        # Max Pain
        # -----------------------------------------------------

        max_pain_result = MaxPainCalculator(
            self.chain
        ).calculate()

        max_pain = float(
            max_pain_result.strike
        )

        max_pain_distance = round(
            max_pain - spot,
            2,
        )

        # -----------------------------------------------------
        # OI Walls
        # -----------------------------------------------------

        put_oi_wall = max(
            relevant,
            key=lambda x: x.put.open_interest,
        )

        call_oi_wall = max(
            relevant,
            key=lambda x: x.call.open_interest,
        )

        put_oi_wall_strike = float(
            put_oi_wall.strike
        )

        call_oi_wall_strike = float(
            call_oi_wall.strike
        )

        # -----------------------------------------------------
        # Change in OI Walls
        # -----------------------------------------------------

        put_change_oi_wall = max(
            relevant,
            key=lambda x: x.put.change_in_oi,
        )

        call_change_oi_wall = max(
            relevant,
            key=lambda x: x.call.change_in_oi,
        )

        put_change_oi_strike = float(
            put_change_oi_wall.strike
        )

        call_change_oi_strike = float(
            call_change_oi_wall.strike
        )

        # -----------------------------------------------------
        # Intelligent Support
        # -----------------------------------------------------

        below_atm = [
            x
            for x in relevant
            if x.strike <= spot
        ]

        above_atm = [
            x
            for x in relevant
            if x.strike >= spot
        ]

        # Put OI below spot is treated as support.
        put_support_candidates = [
            x
            for x in below_atm
            if x.put.open_interest > 0
        ]

        if put_support_candidates:
            support_obj = max(
                put_support_candidates,
                key=lambda x: (
                    x.put.open_interest,
                    x.put.change_in_oi,
                ),
            )
            support = float(
                support_obj.strike
            )
        else:
            support = float(
                below_atm[-1].strike
                if below_atm
                else strikes[0].strike
            )

        # -----------------------------------------------------
        # Strong Support
        # -----------------------------------------------------

        strong_support_candidates = [
            x
            for x in below_atm
            if x.put.change_in_oi > 0
        ]

        if strong_support_candidates:
            strong_support_obj = max(
                strong_support_candidates,
                key=lambda x: (
                    x.put.change_in_oi,
                    x.put.open_interest,
                ),
            )

            strong_support = float(
                strong_support_obj.strike
            )
        else:
            strong_support = support

        # -----------------------------------------------------
        # Intelligent Resistance
        # -----------------------------------------------------

        call_resistance_candidates = [
            x
            for x in above_atm
            if x.call.open_interest > 0
        ]

        if call_resistance_candidates:
            resistance_obj = max(
                call_resistance_candidates,
                key=lambda x: (
                    x.call.open_interest,
                    x.call.change_in_oi,
                ),
            )

            resistance = float(
                resistance_obj.strike
            )
        else:
            resistance = float(
                above_atm[0].strike
                if above_atm
                else strikes[-1].strike
            )

        # -----------------------------------------------------
        # Strong Resistance
        # -----------------------------------------------------

        strong_resistance_candidates = [
            x
            for x in above_atm
            if x.call.change_in_oi > 0
        ]

        if strong_resistance_candidates:
            strong_resistance_obj = max(
                strong_resistance_candidates,
                key=lambda x: (
                    x.call.change_in_oi,
                    x.call.open_interest,
                ),
            )

            strong_resistance = float(
                strong_resistance_obj.strike
            )
        else:
            strong_resistance = resistance

        # -----------------------------------------------------
        # OI Classification
        # -----------------------------------------------------

        oi_results = OIAnalyzer(
            self.chain
        ).analyze()

        relevant_strikes = {
            x.strike
            for x in relevant
        }

        relevant_oi = [
            item
            for item in oi_results
            if item.strike in relevant_strikes
        ]

        bullish_oi = sum(
            1
            for item in relevant_oi
            if item.signal
            in (
                OIType.LONG_BUILDUP,
                OIType.SHORT_COVERING,
            )
        )

        bearish_oi = sum(
            1
            for item in relevant_oi
            if item.signal
            in (
                OIType.SHORT_BUILDUP,
                OIType.LONG_UNWINDING,
            )
        )

        neutral_oi = sum(
            1
            for item in relevant_oi
            if item.signal == OIType.NEUTRAL
        )

        # -----------------------------------------------------
        # Scoring
        # -----------------------------------------------------

        bullish_score = 0
        bearish_score = 0

        # PCR
        if pcr >= 1.20:
            bullish_score += 3
        elif pcr >= 1.00:
            bullish_score += 2
        elif pcr >= 0.80:
            bullish_score += 1
            bearish_score += 1
        else:
            bearish_score += 3

        # OI
        if bullish_oi > bearish_oi:
            bullish_score += 3
        elif bearish_oi > bullish_oi:
            bearish_score += 3

        # Max pain
        if spot < max_pain:
            bullish_score += 1
        elif spot > max_pain:
            bearish_score += 1

        # Put wall below spot
        if put_oi_wall_strike <= spot:
            bullish_score += 1

        # Call wall above spot
        if call_oi_wall_strike >= spot:
            bearish_score += 1

        # -----------------------------------------------------
        # Final Bias
        # -----------------------------------------------------

        score_difference = (
            bullish_score - bearish_score
        )

        total_score = (
            bullish_score
            + bearish_score
        )

        if score_difference >= 3:
            bias = "BULLISH"
        elif score_difference <= -3:
            bias = "BEARISH"
        else:
            bias = "NEUTRAL"

        if total_score:
            confidence = (
                abs(score_difference)
                / total_score
                * 100
            )
        else:
            confidence = 0.0

        confidence = round(
            confidence,
            1,
        )

        # -----------------------------------------------------
        # Trading Action
        # -----------------------------------------------------

        if bias == "BULLISH" and confidence >= 55:
            action = "BUY"

        elif bias == "BEARISH" and confidence >= 55:
            action = "SELL"

        else:
            action = "WAIT"

        # -----------------------------------------------------
        # Entry / Risk Levels
        # -----------------------------------------------------

        if action == "BUY":

            entry = spot

            stop_loss = (
                strong_support
                if strong_support < spot
                else support
            )

            target_1 = resistance

            target_2 = (
                resistance
                + (
                    resistance
                    - support
                )
            )

        elif action == "SELL":

            entry = spot

            stop_loss = (
                strong_resistance
                if strong_resistance > spot
                else resistance
            )

            target_1 = support

            target_2 = (
                support
                - (
                    resistance
                    - support
                )
            )

        else:

            entry = spot

            stop_loss = 0.0

            target_1 = resistance

            target_2 = strong_resistance

        return MarketAnalysis(
            symbol=self.chain.symbol,
            spot=spot,
            expiry=self.chain.expiry,

            atm_strike=atm_strike,

            pcr=pcr,
            pcr_signal=pcr_result.signal,

            max_pain=max_pain,
            max_pain_distance=max_pain_distance,

            support=support,
            strong_support=strong_support,

            resistance=resistance,
            strong_resistance=strong_resistance,

            put_oi_wall=put_oi_wall_strike,
            call_oi_wall=call_oi_wall_strike,

            put_change_oi_wall=put_change_oi_strike,
            call_change_oi_wall=call_change_oi_strike,

            bullish_oi=bullish_oi,
            bearish_oi=bearish_oi,
            neutral_oi=neutral_oi,

            bullish_score=bullish_score,
            bearish_score=bearish_score,

            bias=bias,
            confidence=confidence,

            action=action,

            entry=round(entry, 2),
            stop_loss=round(stop_loss, 2),
            target_1=round(target_1, 2),
            target_2=round(target_2, 2),
        )