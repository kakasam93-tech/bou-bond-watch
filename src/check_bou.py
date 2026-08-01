from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import re

BASE_URL = "https://bou.or.ug"

START_PAGES = [
    "https://bou.or.ug/bouwebsite/FinancialMarkets/",
    "https://bou.or.ug/",
]

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "treasury bond",
    "treasury bonds",
    "t-bill",
    "t-bills",
    "auction",
    "government securities",
]

EXCLUDE = [
    "calculator",
    "sentiment",
    "financial stability",
    "annual report",
    "policy statement",
]

found = []


def interesting(text, url):
    text = (text or "").lower()
    url = (url or "").lower()

    for word in EXCLUDE:
        if word in text or word in url:
            return False

    for word in KEYWORDS:
        if word in text or word in url:
            return True

    if url.endswith(".pdf"):
        if re.search(r"bill|bond|auction", url):
            return True

    return False
    with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    for start_page in START_PAGES:

        print(f"\nOpening {start_page}")

        try:
            page.goto(start_page, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print("Failed:", e)
            continue

        links = page.locator("a").evaluate_all("""
elements => elements.map(a => ({
    text: (a.innerText || "").trim(),
    href: a.href
}))
""")

        print(f"Found {len(links)} links")

        for link in links:

            text = link["text"]
            href = link["href"]

            if not href:
                continue

            href = urljoin(BASE_URL, href)

            if interesting(text, href):
                found.append({
                    "title": text,
                    "url": href
                })

    browser.close()
    print("\n" + "=" * 70)
print("TREASURY SECURITIES FOUND")
print("=" * 70)

seen = set()
count = 0

for item in found:

    key = item["url"].strip().lower()

    if key in seen:
        continue

    seen.add(key)
    count += 1

    print(f"\n[{count}]")
    print("Title :", item["title"] if item["title"] else "(No title)")
    print("URL   :", item["url"])

if count == 0:
    print("\nNo Treasury Bill or Treasury Bond announcements were found.")

print("\nFinished.")
