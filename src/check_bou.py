from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://bou.or.ug"

KEYWORDS = [
    "financial",
    "markets",
    "treasury",
    "bond",
    "bill",
    "auction",
    "tender",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Opening BoU homepage...")

    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    links = page.locator("a").all()

    print(f"Found {len(links)} links\n")

    seen = set()

    for link in links:
        try:
            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if not href:
                continue

            full_url = urljoin(BASE_URL, href)

            combined = f"{text} {full_url}".lower()

            if any(word in combined for word in KEYWORDS):
                if full_url not in seen:
                    seen.add(full_url)
                    print("=" * 60)
                    print("TEXT:", text)
                    print("URL :", full_url)

        except Exception:
            pass

    browser.close()