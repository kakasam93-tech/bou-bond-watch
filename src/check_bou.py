from playwright.sync_api import sync_playwright
from urllib.parse import urljoin

BASE_URL = "https://bou.or.ug"

KEYWORDS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
    "treasury bond",
    "treasury bonds",
    "91-day",
    "182-day",
    "364-day",
    "2-year",
    "3-year",
    "5-year",
    "10-year",
    "15-year",
    "20-year",
    "auction",
    "auction results",
    "invitation",
    "issue no",
]

IGNORE = [
    "calculator",
    "financial stability",
    "sentiment",
    "annual report",
    "research",
    ".pdf",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening BoU homepage...")

    page