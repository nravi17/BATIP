"""
BATIP Trade Candidate Scanner.

Converts trade decisions into ranked trade candidates.

This module does not execute orders and has no broker connectivity.
"""

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class TradeCandidate:
    """A normalized trade candidate."""

    symbol: str
    action: str
    direction: str
    score: float
    confidence: float
    entry: float
    stop_loss: float
    target_1: float
    target_2: float
    position_size: int
    maximum_loss: float
    risk_reward_1: float
    risk_reward_2: float

    @classmethod
    def from_decision(cls, decision: Any) -> "TradeCandidate":
        """Create a candidate from a TradeDecision object."""

        setup = getattr(decision, "setup", None)

        return cls(
            symbol=str(getattr(decision, "symbol", "")),
            action=str(getattr(decision, "trade_action", "AVOID")),
            direction=str(getattr(decision, "direction", "")),
            score=float(getattr(decision, "opportunity_score", 0)),
            confidence=float(getattr(decision, "confidence", 0)),
            entry=float(getattr(setup, "entry", 0)),
            stop_loss=float(getattr(setup, "stop_loss", 0)),
            target_1=float(getattr(setup, "target_1", 0)),
            target_2=float(getattr(setup, "target_2", 0)),
            position_size=int(getattr(setup, "position_size", 0)),
            maximum_loss=float(getattr(setup, "maximum_loss", 0)),
            risk_reward_1=float(getattr(setup, "risk_reward_1", 0)),
            risk_reward_2=float(getattr(setup, "risk_reward_2", 0)),
        )

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "TradeCandidate":
        """Create a candidate from a dictionary."""

        return cls(
            symbol=str(data.get("symbol", "")),
            action=str(data.get("action", "AVOID")),
            direction=str(data.get("direction", "")),
            score=float(
                data.get(
                    "score",
                    data.get("opportunity_score", 0),
                )
            ),
            confidence=float(data.get("confidence", 0)),
            entry=float(data.get("entry", 0)),
            stop_loss=float(data.get("stop_loss", 0)),
            target_1=float(data.get("target_1", 0)),
            target_2=float(data.get("target_2", 0)),
            position_size=int(data.get("position_size", 0)),
            maximum_loss=float(data.get("maximum_loss", 0)),
            risk_reward_1=float(data.get("risk_reward_1", 0)),
            risk_reward_2=float(data.get("risk_reward_2", 0)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation."""

        return {
            "symbol": self.symbol,
            "action": self.action,
            "direction": self.direction,
            "score": self.score,
            "confidence": self.confidence,
            "entry": self.entry,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "position_size": self.position_size,
            "maximum_loss": self.maximum_loss,
            "risk_reward_1": self.risk_reward_1,
            "risk_reward_2": self.risk_reward_2,
        }


class CandidateScanner:
    """Filter and rank trade candidates."""

    ACTION_PRIORITY = {
        "TRADE": 2,
        "WATCH": 1,
        "AVOID": 0,
    }

    def create(self, candidate: Any) -> TradeCandidate:
        """Normalize a candidate."""

        if isinstance(candidate, TradeCandidate):
            return candidate

        if isinstance(candidate, dict):
            return TradeCandidate.from_mapping(candidate)

        return TradeCandidate.from_decision(candidate)

    def scan(
        self,
        candidates: Iterable[Any],
    ) -> list[TradeCandidate]:
        """Normalize, filter and rank candidates."""

        normalized = [
            self.create(candidate)
            for candidate in candidates
        ]

        filtered = [
            candidate
            for candidate in normalized
            if candidate.action.upper() != "AVOID"
        ]

        return sorted(
            filtered,
            key=self._ranking_key,
            reverse=True,
        )

    def top_n(
        self,
        candidates: Iterable[Any],
        n: int,
    ) -> list[TradeCandidate]:
        """Return the highest-ranked N candidates."""

        if n <= 0:
            return []

        return self.scan(candidates)[:n]

    def trade_candidates(
        self,
        candidates: Iterable[Any],
    ) -> list[TradeCandidate]:
        """Return only candidates marked TRADE."""

        return [
            candidate
            for candidate in self.scan(candidates)
            if candidate.action.upper() == "TRADE"
        ]

    @classmethod
    def _ranking_key(
        cls,
        candidate: TradeCandidate,
    ) -> tuple[float, float, float]:
        """Build the candidate ranking key."""

        action_priority = cls.ACTION_PRIORITY.get(
            candidate.action.upper(),
            0,
        )

        return (
            float(action_priority),
            candidate.score,
            candidate.confidence,
        )


def scan_candidates(
    candidates: Iterable[Any],
) -> list[TradeCandidate]:
    """Convenience function for candidate scanning."""

    return CandidateScanner().scan(candidates)


def top_candidates(
    candidates: Iterable[Any],
    n: int,
) -> list[TradeCandidate]:
    """Convenience function for retrieving top candidates."""

    return CandidateScanner().top_n(candidates, n)