"""
BATIP Stock Signal Engine.

Combines price, momentum, volume, sector, and liquidity
scores into a deterministic stock signal.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StockSignalSnapshot:
    """Normalized stock signal snapshot."""

    symbol: str

    price_score: int
    momentum_score: int
    volume_score: int
    sector_score: int
    liquidity_score: int

    total_score: int = 0
    direction: str = "Neutral"
    signal: str = "WATCH"
    confidence: str = "Low"


class StockSignalEngine:
    """Generate deterministic stock trading signals."""

    @staticmethod
    def direction_from_score(total_score: int) -> str:
        """Convert total score into market direction."""

        score = int(total_score)

        if score > 0:
            return "Bullish"

        if score < 0:
            return "Bearish"

        return "Neutral"

    @staticmethod
    def signal_from_score(total_score: int) -> str:
        """
        Convert total score into a trading signal.

        Score range is -10 to +10.

        >= +7 -> STRONG BUY
        >= +5 -> BUY
        >  -5 -> WATCH
        <= -5 -> SELL
        <= -7 -> STRONG SELL
        """

        score = int(total_score)

        if score >= 7:
            return "STRONG BUY"

        if score >= 5:
            return "BUY"

        if score <= -7:
            return "STRONG SELL"

        if score <= -5:
            return "SELL"

        return "WATCH"

    @staticmethod
    def confidence_from_score(total_score: int) -> str:
        """Convert total score into signal confidence."""

        score = abs(int(total_score))

        if score >= 5:
            return "High"

        if score >= 3:
            return "Medium"

        return "Low"

    def analyze(
        self,
        signal: StockSignalSnapshot,
    ) -> StockSignalSnapshot:
        """Generate a stock signal from component scores."""

        if signal is None:
            raise ValueError("signal cannot be None")

        total_score = (
            int(signal.price_score)
            + int(signal.momentum_score)
            + int(signal.volume_score)
            + int(signal.sector_score)
            + int(signal.liquidity_score)
        )

        direction = self.direction_from_score(total_score)
        trading_signal = self.signal_from_score(total_score)
        confidence = self.confidence_from_score(total_score)

        return StockSignalSnapshot(
            symbol=signal.symbol,
            price_score=int(signal.price_score),
            momentum_score=int(signal.momentum_score),
            volume_score=int(signal.volume_score),
            sector_score=int(signal.sector_score),
            liquidity_score=int(signal.liquidity_score),
            total_score=total_score,
            direction=direction,
            signal=trading_signal,
            confidence=confidence,
        )