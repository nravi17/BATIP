import re
import requests

BASE = "https://www.nseindia.com"

JS_FILES = [
    "/dist/js/sections/option-chain-v3.js?v=07082026",
    "/dist/js/sections/option-chainstream.js?v=07082026",
    "/dist/js/components/option-chain/option-chain-table-v2.js?v=07082026",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
}

session = requests.Session()

home = session.get(
    BASE,
    headers=HEADERS,
    timeout=15,
)

print("HOME:", home.status_code)

page = session.get(
    BASE + "/option-chain",
    headers={
        **HEADERS,
        "Referer": BASE + "/",
    },
    timeout=15,
)

print("OPTION CHAIN:", page.status_code)
print()

patterns = [
    r'https?://[^"\']+',
    r'/api/[^"\']+',
    r'api/[^"\']+',
    r'option-chain[^"\']+',
    r'optionChain[^"\']+',
    r'fetch\([^)]{0,500}\)',
    r'\.get\([^)]{0,500}\)',
    r'axios[^;]{0,500}',
    r'url\s*:\s*["\'][^"\']+',
]

for js_path in JS_FILES:
    url = BASE + js_path

    print("=" * 80)
    print("JS:", url)

    r = session.get(
        url,
        headers={
            **HEADERS,
            "Referer": BASE + "/option-chain",
        },
        timeout=15,
    )

    print("STATUS:", r.status_code)
    print("LENGTH:", len(r.text))

    if r.status_code != 200:
        continue

    text = r.text

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE,
        )

        if matches:
            print()
            print("PATTERN:", pattern)

            seen = set()

            for match in matches:
                match = match.strip()

                if match not in seen:
                    seen.add(match)
                    print(match[:1000])