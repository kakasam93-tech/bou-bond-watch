from playwright.sync_api import sync_playwright

URL = "https://bou.or.ug"

KEYWORDS = [
    "financial",
    "market",
    "treasury",
    "bond",
    "bill",
    "tender",
    "auction"
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening BoU homepage...")
    page.goto(URL, wait_until="networkidle")

    links = page.locator("a").all()

    print(f"Scanning {len(links)} links...\n")

    seen = set()

    for link in links:
        try:
            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if not href:
                continue

            combined = (text + " " + href).lower()

            if any(word in combined for word in KEYWORDS):
                if href not in seen:
                    seen.add(href)
                    print("=" * 60)
                    print("TEXT :", text)
                    print("LINK :", href)
        except:
            pass

    browser.close()