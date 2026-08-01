from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse

BASE_URL = "https://bou.or.ug"

START_PAGES = [
    "https://bou.or.ug/",
    "https://bou.or.ug/financial-markets/",
]

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
    "treasury bond",
    "treasury bonds",
    "government securities",
    "auction",
]

EXCLUDE = [
    "calculator",
    "exchange rate",
    "interest rate",
    "career",
    "vacancy",
    "procurement",
]


def interesting(title, url):
    title = title.lower()
    url = url.lower()

    for word in EXCLUDE:
        if word in title or word in url:
            return False

    for word in KEYWORDS:
        if word in title or word in url:
            return True

    if url.endswith(".pdf"):
        if any(k in url for k in ["bill", "bond", "auction"]):
            return True

    return False


def crawl():
    results = []
    visited = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        queue = START_PAGES.copy()

        while queue:

            current = queue.pop(0)

            if current in visited:
                continue

            visited.add(current)

            print(f"Scanning {current}")

            try:
                page.goto(current, wait_until="networkidle", timeout=60000)
            except Exception:
                continue

            links = page.locator("a").evaluate_all("""
elements => elements.map(e => ({
title: e.innerText,
href: e.href
}))
""")

            for item in links:

                href = item.get("href", "")
                title = item.get("title", "").strip()

                if not href.startswith(BASE_URL):
                    continue

                if interesting(title, href):

                    results.append({
                        "title": title if title else "(No title)",
                        "url": href
                    })

                if href.startswith(BASE_URL):

                    path = urlparse(href).path

                    if (
                        "/financial-markets" in path
                        or "/treasury" in path
                        or "/markets" in path
                        or "/news" in path
                    ):
                        if href not in visited:
                            queue.append(href)

        browser.close()

    unique = []

    seen = set()

    for item in results:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique 