import json
import os
import re
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

START_URLS = [
    "https://bou.or.ug/",
    "https://bou.or.ug/financial-markets/",
]

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "treasury bond",
    "treasury bonds",
    "tb auction",
    "bond auction",
    "auction results",
    "auction",
]

DATA_FILE = "data/seen.json"


def load_seen():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seen(data):
    os.makedirs("data", exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def interesting(title):
    title = title.lower()

    for word in KEYWORDS:
        if word in title:
            return True

    return False


def scrape():

    seen = load_seen()
    new_items = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        for url in START_URLS:

            print(f"Searching {url}")

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)

                html = page.content()

                soup = BeautifulSoup(html, "lxml")

                links = soup.find_all("a", href=True)

                print(f"Found {len(links)} links")

                for link in links:

                    text = link.get_text(" ", strip=True)
                    href = urljoin(url, link["href"])

                    combined = (text + " " + href).lower()

                    if not interesting(combined):
                        continue

                    if href in seen:
                        continue

                    print("=" * 60)
                    print("NEW TREASURY ANNOUNCEMENT")
                    print(text)
                    print(href)
                    print("=" * 60)

                    new_items.append(href)
                    seen.append(href)

            except Exception as e:
                print(e)

        browser.close()

    save_seen(seen)

    if not new_items:
        print("\nNo new Treasury Bill/Bond announcements found.")

    print("\nFinished.")


if __name__ == "__main__":
    scrape()