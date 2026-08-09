"""
BATIP Strategy Signal Bridge.

Converts StrategyEngine TradingSignal objects into
higher-level BATIP trading inputs.

No broker connectivity.
No real-money execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from batip.trading.strategy import (
    StrategyEngine,
    TradingSignal,
)


@dataclass(frozen=True, slots=True)
class SignalBridgeResult:
    """Result of converting a strategy signal."""

    signal: TradingSignal

    stock_score: int
    technical_score: int
    market_score: int
    sector_score: int


class StrategySignalBridge:
    """Bridge StrategyEngine signals into BATIP."""

    @staticmethod
    def _score_to_int(
        value: float,
    ) -> int:

        return max(
            -10,
            min(
                10,
                int(round(float(value))),
            ),
        )

    @classmethod
    def from_signal(
        cls,
        signal: TradingSignal,
        *,
        stock_score: int,
        technical_score: int,
        market_score: int,
        sector_score: int,
    ) -> SignalBridgeResult:

        if not isinstance(
            signal,
            TradingSignal,
        ):
            raise TypeError(
                "signal must be a TradingSignal"
            )

        return SignalBridgeResult(
            signal=signal,
            stock_score=cls._score_to_int(
                stock_score
            ),
            technical_score=cls._score_to_int(
                technical_score
            ),
            market_score=cls._score_to_int(
                market_score
            ),
            sector_score=cls._score_to_int(
                sector_score
            ),
        )

    @classmethod
    def generate(
        cls,
        *,
        symbol: str,
        direction: str,
        entry: float,
        stop_loss: float,
        target_1: float,
        target_2: float,
        trend_score: float = 0.0,
        momentum_score: float = 0.0,
        volume_score: float = 0.0,
        minimum_risk_reward: float = 1.5,
    ) -> TradingSignal | None:

        return StrategyEngine.evaluate(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            target_1=target_1,
            target_2=target_2,
            trend_score=trend_score,
            momentum_score=momentum_score,
            volume_score=volume_score,
            minimum_risk_reward=minimum_risk_reward,
        )