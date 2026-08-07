from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import FINANCIAL_MARKETS_URL, KEYWORDS
from models import BondTender


def find_latest_bond() -> Optional[BondTender]:
    """
    Find the latest Treasury Bond Invitation to Tender
    published on the Bank of Uganda Financial Markets page.

    Returns:
        BondTender if a suitable tender is found.
        None if no tender is found.
    """

    try:
        response = requests.get(
            FINANCIAL_MARKETS_URL,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
                )
            },
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Unable to access Bank of Uganda website: {error}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    candidates = []

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)
        href = link.get("href", "").strip()

        if not href:
            continue

        full_url = urljoin(FINANCIAL_MARKETS_URL, href)

        searchable_text = f"{title} {full_url}".lower()

        has_treasury_bond = (
            "treasury bond" in searchable_text
            or "treasury bonds" in searchable_text
        )

        has_tender = (
            "invitation to tender" in searchable_text
            or "tender" in searchable_text
        )

        is_pdf = full_url.lower().endswith(".pdf")

        if has_treasury_bond and (has_tender or is_pdf):

            candidates.append(
                BondTender(
                    title=title or "Treasury Bond Invitation to Tender",
                    pdf_url=full_url,
                )
            )

    if not candidates:
        print("No Treasury Bond Invitation to Tender found.")
        return None

    # The Financial Markets page normally presents the newest
    # announcements first, so use the first matching candidate.
    latest = candidates[0]

    print("\nTreasury Bond Invitation Found")
    print(f"Title: {latest.title}")
    print(f"PDF:   {latest.pdf_url}")

    return latest
