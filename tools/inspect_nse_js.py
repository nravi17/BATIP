import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE = "https://www.nseindia.com"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
}


session = requests.Session()

home = session.get(
    BASE,
    headers=headers,
    timeout=15,
)

print("HOME:", home.status_code)

page = session.get(
    f"{BASE}/option-chain",
    headers={
        **headers,
        "Referer": f"{BASE}/",
    },
    timeout=15,
)

print("OPTION CHAIN:", page.status_code)
print("HTML LENGTH:", len(page.text))

soup = BeautifulSoup(
    page.text,
    "html.parser",
)

scripts = []

for script in soup.find_all("script"):
    src = script.get("src")

    if src:
        scripts.append(
            urljoin(BASE, src)
        )

print()
print("SCRIPT COUNT:", len(scripts))
print()
print("JAVASCRIPT FILES")
print("=" * 80)

for url in scripts:
    print(url)

print()
print("POSSIBLE OPTION/MARKET JS")
print("=" * 80)

for url in scripts:
    lower = url.lower()

    if (
        "option" in lower
        or "market" in lower
        or "chunk" in lower
        or "main" in lower
    ):
        print(url)