"""
BATIP NSE endpoint diagnostic.

This script does not modify BATIP application state.
It only checks which NSE pages/endpoints are reachable.
"""

import requests


BASE_URL = "https://www.nseindia.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def main() -> None:
    session = requests.Session()

    session.headers.update(HEADERS)

    print("=" * 70)
    print("BATIP NSE ENDPOINT DIAGNOSTIC")
    print("=" * 70)

    # ---------------------------------------------------------
    # Homepage
    # ---------------------------------------------------------

    response = session.get(
        BASE_URL,
        timeout=15,
    )

    print()
    print("NSE HOME")
    print("Status:", response.status_code)
    print("URL:", response.url)

    # ---------------------------------------------------------
    # Option Chain page
    # ---------------------------------------------------------

    option_chain_url = (
        f"{BASE_URL}/option-chain"
    )

    response = session.get(
        option_chain_url,
        timeout=15,
        headers={
            **HEADERS,
            "Referer": BASE_URL + "/",
        },
    )

    print()
    print("OPTION CHAIN PAGE")
    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Content-Length:", len(response.content))

    # ---------------------------------------------------------
    # Current API endpoint
    # ---------------------------------------------------------

    api_url = (
        f"{BASE_URL}/api/option-chain-indices"
    )

    response = session.get(
        api_url,
        params={
            "symbol": "BANKNIFTY",
        },
        timeout=15,
        headers={
            **HEADERS,
            "Accept": "application/json, text/plain, */*",
            "Referer": option_chain_url,
        },
    )

    print()
    print("OPTION CHAIN API")
    print("Status:", response.status_code)
    print("URL:", response.url)
    print("Content-Type:", response.headers.get("Content-Type"))

    print()
    print("COOKIES")
    print(list(session.cookies.keys()))

    print()
    print("RESPONSE PREVIEW")
    print(response.text[:500])

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()