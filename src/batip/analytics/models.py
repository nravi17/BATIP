"""
Common analytics result models.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class AnalyticsResult:
    name: str
    value: float
    signal: str
    description: str