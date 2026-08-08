"""
BATIP NSE HTTP Client

Browser-like HTTP client for NSE.

Important:
This client explicitly avoids requesting Brotli-compressed
responses (Content-Encoding: br). NSE is asked for gzip/deflate
only, so responses can be parsed without manual decompression.
"""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

from batip.config import settings
from batip.core.exceptions import NetworkError


logger = logging.getLogger(__name__)


class NSEHttpClient:
    """HTTP client for NSE APIs."""

    def __init__(self) -> None:
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": settings.USER_AGENT,
                "Accept": (
                    "application/json, "
                    "text/plain, */*"
                ),
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": (
                    "en-US,en;q=0.9"
                ),
                "Referer": settings.NSE_OPTION_CHAIN_PAGE,
                "Connection": "keep-alive",
            }
        )

        self._initialize_session()

    # ---------------------------------------------------------
    # Session initialization
    # ---------------------------------------------------------

    def _initialize_session(self) -> None:
        """Initialize NSE browser-like session."""

        logger.info(
            "Initializing NSE browser-like session"
        )

        try:
            response = self.session.get(
                settings.NSE_BASE_URL,
                headers={
                    "User-Agent": settings.USER_AGENT,
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,*/*;q=0.8"
                    ),
                    "Accept-Language": (
                        "en-US,en;q=0.9"
                    ),
                    "Accept-Encoding": "gzip, deflate",
                },
                timeout=settings.REQUEST_TIMEOUT,
            )

            logger.info(
                "NSE homepage status: %s",
                response.status_code,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise NetworkError(
                f"Unable to initialize NSE session: {exc}"
            ) from exc

        # Visit option-chain page to obtain cookies
        try:
            response = self.session.get(
                settings.NSE_OPTION_CHAIN_PAGE,
                headers={
                    "User-Agent": settings.USER_AGENT,
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,*/*;q=0.8"
                    ),
                    "Accept-Language": (
                        "en-US,en;q=0.9"
                    ),
                    "Accept-Encoding": "gzip, deflate",
                    "Referer": settings.NSE_BASE_URL,
                },
                timeout=settings.REQUEST_TIMEOUT,
            )

            logger.info(
                "NSE option-chain page status: %s",
                response.status_code,
            )

        except requests.RequestException as exc:
            raise NetworkError(
                f"Unable to initialize NSE option-chain session: {exc}"
            ) from exc

        logger.info(
            "NSE session cookies: %s",
            list(self.session.cookies.keys()),
        )

        logger.info(
            "NSE session initialized successfully"
        )

    # ---------------------------------------------------------
    # JSON parsing
    # ---------------------------------------------------------

    def _parse_json(self, response):
        """
        Safely parse an NSE JSON response.
        """

        content_encoding = response.headers.get(
            "Content-Encoding",
            "",
        ).lower()

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        logger.info(
            "JSON response: status=%s encoding=%s "
            "content-type=%s bytes=%s",
            response.status_code,
            content_encoding,
            content_type,
            len(response.content),
        )

        try:
            return response.json()

        except ValueError as exc:
            preview = response.text[:500]

            raise NetworkError(
                "NSE returned invalid JSON. "
                f"HTTP={response.status_code}, "
                f"Content-Type={content_type}, "
                f"Content-Encoding={content_encoding}, "
                f"Length={len(response.content)}, "
                f"Preview={preview!r}"
            ) from exc

    # ---------------------------------------------------------
    # GET JSON
    # ---------------------------------------------------------

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """GET JSON data from NSE."""

        last_error: Exception | None = None

        for attempt in range(
            1,
            settings.MAX_RETRIES + 1,
        ):
            logger.info(
                "GET attempt %s/%s: %s",
                attempt,
                settings.MAX_RETRIES,
                url,
            )

            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers={
                        "User-Agent": settings.USER_AGENT,
                        "Accept": (
                            "application/json, "
                            "text/plain, */*"
                        ),
                        "Accept-Language": (
                            "en-US,en;q=0.9"
                        ),
                        "Accept-Encoding": "gzip, deflate",
                        "Referer": (
                            settings.NSE_OPTION_CHAIN_PAGE
                        ),
                        "Connection": "keep-alive",
                    },
                    timeout=settings.REQUEST_TIMEOUT,
                )

                logger.info(
                    "Status Code: %s",
                    response.status_code,
                )

                logger.info(
                    "Final URL: %s",
                    response.url,
                )

                logger.info(
                    "Content-Type: %s",
                    response.headers.get(
                        "Content-Type"
                    ),
                )

                logger.info(
                    "Content-Encoding: %s",
                    response.headers.get(
                        "Content-Encoding"
                    ),
                )

                if response.status_code == 404:
                    raise NetworkError(
                        "NSE endpoint returned HTTP 404: "
                        f"{response.url}"
                    )

                if response.status_code == 429:
                    raise NetworkError(
                        "NSE rate limit returned HTTP 429."
                    )

                if response.status_code >= 500:
                    raise NetworkError(
                        "NSE server error: "
                        f"HTTP {response.status_code}"
                    )

                response.raise_for_status()

                payload = self._parse_json(
                    response
                )

                logger.info(
                    "NSE request successful"
                )

                return payload

            except (
                requests.RequestException,
                NetworkError,
            ) as exc:

                last_error = exc

                logger.warning(
                    "NSE request failed: %s",
                    exc,
                )

                if attempt < settings.MAX_RETRIES:
                    sleep_seconds = attempt
                    time.sleep(sleep_seconds)

        raise NetworkError(
            "NSE request failed after "
            f"{settings.MAX_RETRIES} attempts: "
            f"{last_error}"
        ) from last_error