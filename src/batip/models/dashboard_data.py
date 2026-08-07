"""
BATIP Dashboard View Model
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DashboardData:
    """
    View model containing all data required by the dashboard.

    The dashboard should consume this object instead of dealing
    directly with individual analytics/service results.
    """

    chain: Any
    pcr: Any
    max_pain: Any
    support: Any