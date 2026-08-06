"""
Reusable HTTP client for BATIP providers.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from batip.config import settings
from batip.core.exceptions import NetworkError
from batip.logs.logger import logger


class BaseHttpClient:
    """Reusable HTTP client."""

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": settings.USER_AGENT,
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
            }
        )

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        last_exception = None

        for attempt in range(settings.MAX_RETRIES):

            try:

                logger.info("GET %s", url)

                response = self.session.get(
                    url,
                    params=params,
                    timeout=settings.REQUEST_TIMEOUT,
                )

                response.raise_for_status()

                logger.info(
                    "Success %s",
                    response.status_code,
                )

                return response.json()

            except Exception as exc:

                logger.exception(exc)

                last_exception = exc

                time.sleep(attempt + 1)

        raise NetworkError(
            f"Failed request: {url}"
        ) from last_exception