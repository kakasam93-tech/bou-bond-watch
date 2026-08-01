import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://bou.or.ug"

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
    "treasury bond",
    "treasury bonds",
    "auction",
    "auction results",
    "91-day",
    "182-day",
    "364-day",
    "2-year",
    "3-year",
    "5-year",
    "10-year",
    "15-year",
    "20-year",
]

IGNORE = [
    "calculator",
    "research",
    "financial stability",
    "sentiment",
    ".pdf",
]

print("Connecting to BoU...")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(BASE_URL, headers=headers, timeout=30)
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

    full_url = urljoin(BASE_URL, href)

    combined = f"{text} {full_url}".lower()

    if (
        any(k in combined for k in KEYWORDS)
        and not any(i in combined for i in IGNORE)
    ):
        if full_url not in seen:
            seen.add(full_url)
            found = True

            print("=" * 60)
            print("NEW TREASURY SECURITY FOUND")
            print("Title :", text)
            print("URL   :", full_url)

if not found:
    print("No Treasury Bill/Bond announcements found.")

print("Finished.")