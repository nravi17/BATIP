"""
HTTP client for NSE endpoints.

Responsibilities:
- Create and reuse a requests.Session
- Initialize NSE cookies
- Apply common headers
- Retry transient failures
"""

from __future__ import annotations

import time
from typing import Any

import requests

from batip.config import settings


class NSEHttpClient:
    """Reusable HTTP client for NSE."""

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": settings.USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": settings.NSE_BASE_URL,
                "Connection": "keep-alive",
            }
        )

        self._initialize_session()

    def _initialize_session(self) -> None:
        """
        Visit the NSE homepage once so the session receives
        the cookies required for later API requests.
        """

        response = self.session.get(
            settings.NSE_BASE_URL,
            timeout=settings.REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    def get_json(self, url: str, params: dict | None = None) -> dict[str, Any]:
        """
        Execute a GET request and return JSON.
        """

        last_exception = None

        for attempt in range(settings.MAX_RETRIES):

            try:

                response = self.session.get(
                    url,
                    params=params,
                    timeout=settings.REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                return response.json()

            except Exception as exc:

                last_exception = exc

                time.sleep(1)

        raise RuntimeError(
            f"Failed after {settings.MAX_RETRIES} retries"
        ) from last_exception