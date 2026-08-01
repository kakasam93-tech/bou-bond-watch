import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://bou.or.ug"

START_PAGES = [
    "https://bou.or.ug",
    "https://bou.or.ug/financial-markets/",
]

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
    "treasury bond",
    "treasury bonds",
    "bond auction",
    "bill auction",
    "auction results",
    "government securities",
]

EXCLUDE = [
    "calculator",
    "interest rates",
    "exchange rates",
    "careers",
    "vacancies",
    "procurement",
    "press release",
    "monetary policy",
]


def interesting(text, url):
    text = text.lower()
    url = url.lower()

    for word in EXCLUDE:
        if word in text or word in url:
            return False

    for word in KEYWORDS:
        if word in text or word in url:
            return True

    if url.endswith(".pdf"):
        if re.search(r"(bill|bond|auction|security)", url):
            return True

    return False


found = []

visited = set()

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

print("Searching Bank of Uganda...")

for start in START_PAGES:

    try:
        response = session.get(start, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Cannot open {start}")
        print(e)
        continue

    soup = BeautifulSoup(response.text, "lxml")

    links = soup.find_all("a", href=True)

    print(f"{start} -> {len(links)} links")

    for link in links:

        href = urljoin(BASE_URL, link["href"])

        if href in visited:
            continue

        visited.add(href)

        text = link.get_text(" ", strip=True)

        if interesting(text, href):
            found.append({
                "title": text if text else "(No title)",
                "url": href
            })

        if href.startswith(BASE_URL):

            try:
                page = session.get(href, timeout=10)

                if "text/html" not in page.headers.get("Content-Type", ""):
                    continue

                inner = BeautifulSoup(page.text, "lxml")

                for a in inner.find_all("a", href=True):

                    url = urljoin(BASE_URL, a["href"])

                    if url in visited:
                        continue

                    visited.add(url)

                    title = a.get_text(" ", strip=True)

                    if interesting(title, url):
                        found.append({
                            "title": title if title else "(No title)",
                            "url": url
                        })

            except:
                pass


# Remove duplicates
unique = []
seen = set()

for item in found:
    key = item["url"]

    if key not in seen:
        seen.add(key)
        unique.append(item)

print("\n" + "=" * 70)

if unique:
    print(f"FOUND {len(unique)} TREASURY SECURITY LINKS\n")

    for item in unique:
        print(f"Title : {item['title']}")
        print(f"URL   : {item['url']}")
        print("-" * 70)

else:
    print("No Treasury Bill/Bond announcements found.")

print("\nFinished.")
