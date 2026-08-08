"""
BATIP NSE Market Data Provider

Live NSE option-chain provider.

Current NSE endpoint:
    /api/option-chain-v3

Expiry discovery:
    /api/option-chain-contract-info

The provider:
1. Discovers NSE expiries.
2. Selects the nearest valid future expiry.
3. Requests option-chain-v3 using that expiry.
4. Falls back to configured expiry if discovery fails.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from batip.config import settings
from batip.core.exceptions import NetworkError
from batip.data.http_client import NSEHttpClient
from batip.providers.base_provider import MarketDataProvider
from batip.providers.nse_parser import NSEParser


class NSEProvider(MarketDataProvider):
    """
    Live market-data provider for NSE.
    """

    def __init__(self) -> None:
        self.client = NSEHttpClient()
        self.parser = NSEParser()

    # ---------------------------------------------------------
    # Endpoint helpers
    # ---------------------------------------------------------

    def _option_chain_url(self) -> str:
        return settings.OPTION_CHAIN_URL

    def _contract_info_url(self) -> str:
        return settings.NSE_OPTION_CHAIN_CONTRACT_INFO_URL

    # ---------------------------------------------------------
    # Expiry discovery
    # ---------------------------------------------------------

    def _get_expiry_candidates(
        self,
        symbol: str,
    ) -> list[str]:
        """
        Discover valid future expiries from NSE.

        Uses option-chain-contract-info.

        If the endpoint fails, fall back to
        NSE_DEFAULT_EXPIRY.
        """

        contract_info_url = self._contract_info_url()

        try:
            payload = self.client.get_json(
                contract_info_url,
                params={
                    "symbol": symbol,
                },
            )

            if not isinstance(payload, dict):
                raise NetworkError(
                    "NSE contract-info response is not a JSON object"
                )

            expiry_dates = payload.get(
                "expiryDates",
                [],
            )

            if not expiry_dates:
                raise NetworkError(
                    f"NSE returned no expiry dates for {symbol}"
                )

            valid_expiries: list[tuple[datetime, str]] = []

            for expiry in expiry_dates:

                if not isinstance(expiry, str):
                    continue

                try:
                    parsed = datetime.strptime(
                        expiry,
                        "%d-%b-%Y",
                    )

                    valid_expiries.append(
                        (parsed, expiry)
                    )

                except ValueError:
                    continue

            today = datetime.now().date()

            future_expiries = [
                item
                for item in valid_expiries
                if item[0].date() >= today
            ]

            future_expiries.sort(
                key=lambda item: item[0]
            )

            if future_expiries:
                result = [
                    expiry
                    for _, expiry in future_expiries
                ]

                return result

            raise NetworkError(
                f"NSE returned no future expiries for {symbol}"
            )

        except Exception as exc:

            fallback = settings.NSE_DEFAULT_EXPIRY

            if fallback:
                print(
                    f"WARNING: NSE expiry discovery failed: {exc}"
                )

                print(
                    f"WARNING: Using fallback expiry: {fallback}"
                )

                return [fallback]

            raise NetworkError(
                f"Unable to discover NSE expiries "
                f"for {symbol}: {exc}"
            ) from exc

    # ---------------------------------------------------------
    # Fetch option chain
    # ---------------------------------------------------------

    def fetch_payload(
        self,
        symbol: str = "BANKNIFTY",
    ) -> dict[str, Any]:
        """
        Fetch raw NSE option-chain data.
        """

        expiry_candidates = self._get_expiry_candidates(
            symbol
        )

        errors: list[str] = []

        endpoint = self._option_chain_url()

        for expiry in expiry_candidates:

            try:

                print(
                    f"Fetching NSE option chain: "
                    f"{symbol} / {expiry}"
                )

                payload = self.client.get_json(
                    endpoint,
                    params={
                        "type": "Indices",
                        "symbol": symbol,
                        "expiry": expiry,
                    },
                )

                if not isinstance(payload, dict):
                    raise NetworkError(
                        "NSE returned non-object JSON"
                    )

                records = payload.get(
                    "records",
                    {},
                )

                if not isinstance(records, dict):
                    raise NetworkError(
                        "NSE response missing records object"
                    )

                data = records.get(
                    "data",
                    [],
                )

                if not data:
                    raise NetworkError(
                        "NSE returned empty option-chain "
                        f"data for {symbol} "
                        f"expiry {expiry}"
                    )

                print(
                    f"NSE option chain received: "
                    f"{len(data)} records"
                )

                return payload

            except NetworkError as exc:

                errors.append(
                    f"{expiry}: {exc}"
                )

        raise NetworkError(
            "All NSE expiry candidates failed. "
            + " | ".join(errors)
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def get_option_chain(
        self,
        symbol: str = "BANKNIFTY",
    ):
        """
        Fetch and parse live NSE option-chain data.
        """

        payload = self.fetch_payload(
            symbol=symbol,
        )

        chain = self.parser.parse_option_chain(
            payload
        )

        chain.source = "NSE"
        chain.data_status = "LIVE"

        return chain