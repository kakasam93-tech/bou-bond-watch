import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://bou.or.ug/financial_market"
ROOT_URL = "https://bou.or.ug"

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
    "treasury bond",
    "treasury bonds",
    "auction",
    "auction results",
    "auction calendar",
    "invitation",
    "invitation to tender",
    "91-day",
    "182-day",
    "364-day",
    "2-year",
    "3-year",
    "5-year",
    "10-year",
    "15-year",
    "20-year",
    "government securities",
]

IGNORE = [
    "calculator",
    "financial stability",
    "research",
    "sentiment",
]

print("Connecting to BoU Financial Markets page...")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    BASE_URL,
    headers=headers,
    timeout=30,
)

response.raise_for_status()

print("Connected.")

soup = BeautifulSoup(response.text, "lxml")

links = soup.find_all("a")

print(f"Found {len(links)} links")

seen = set()
found = False

for link in links:

    text = link.get_text(" ", strip=True)
    href = link.get("href")

    if not href:
        continue

    full_url = urljoin(ROOT_URL, href)

    combined = f"{text} {full_url}".lower()

    if (
        any(keyword in combined for keyword in KEYWORDS)
        and not any(ignore in combined for ignore in IGNORE)
    ):

        if full_url not in seen:
            seen.add(full_url)
            found = True

            print("=" * 60)
            print("NEW TREASURY SECURITY FOUND")
            print("Title :", text)
            print("URL   :", full_url)

if not found:
    print("=" * 60)
    print("No Treasury Bill/Bond announcements found.")

print("Finished.")