import re
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BOU_FINANCIAL_MARKETS_URL = "https://bou.or.ug/financial-markets/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    )
}

# Terms that strongly indicate a Treasury Bond tender document.
TREASURY_BOND_TERMS = [
    "treasury bond",
    "treasury bonds",
    "government treasury bond",
    "government treasury bonds",
    "invitation to tender",
    "scheduled auction",
]

# Terms that should cause us to reject unrelated documents.
EXCLUDE_TERMS = [
    "treasury bill",
    "treasury bills",
]


def normalize(text: str) -> str:
    """Normalize text for reliable keyword matching."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def is_treasury_bond_tender(title: str, url: str) -> bool:
    """
    Determine whether a document/link appears to be
    a Bank of Uganda Treasury Bond Invitation to Tender.
    """

    search_text = normalize(f"{title} {url}")

    # Reject Treasury Bill documents.
    if any(term in search_text for term in EXCLUDE_TERMS):
        return False

    # A Treasury Bond document should contain treasury-bond language.
    has_bond = (
        "treasury bond" in search_text
        or "treasury bonds" in search_text
        or "government treasury bond" in search_text
        or "government treasury bonds" in search_text
    )

    if not has_bond:
        return False

    # Prefer actual tender/auction documents.
    has_tender_language = (
        "invitation to tender" in search_text
        or "scheduled auction" in search_text
        or "tender" in search_text
        or "auction" in search_text
    )

    return has_tender_language


def extract_date(text: str) -> Optional[str]:
    """Extract a likely date from a document title/link."""

    patterns = [
        # 13 May 2026
        r"\b\d{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b",

        # 13-May-2026 / 13 May 2026 variants
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",

        # 2026-05-13
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)

    return None


def find_latest_tender() -> Optional[dict]:
    """
    Search the official Bank of Uganda Financial Markets page
    for Treasury Bond Invitation to Tender documents.

    Returns the first matching document or None.
    """

    print("Checking official Bank of Uganda Financial Markets page...")

    try:
        response = requests.get(
            BOU_FINANCIAL_MARKETS_URL,
            headers=HEADERS,
            timeout=30,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"Unable to access Bank of Uganda website: {exc}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    candidates = []

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        href = link.get("href", "").strip()

        if not href:
            continue

        url = urljoin(BOU_FINANCIAL_MARKETS_URL, href)

        combined_text = normalize(f"{title} {url}")

        # We only care about PDF documents or obvious tender links.
        is_pdf = url.lower().split("?")[0].endswith(".pdf")

        if not is_pdf and not any(
            word in combined_text
            for word in ["tender", "auction", "treasury bond"]
        ):
            continue

        if is_treasury_bond_tender(title, url):
            candidates.append(
                {
                    "title": title or "Treasury Bond Invitation to Tender",
                    "url": url,
                    "date": extract_date(f"{title} {url}"),
                }
            )

    if not candidates:
        print("No Treasury Bond Invitation to Tender found.")
        return None

    # Remove duplicate URLs while preserving order.
    unique = []
    seen = set()

    for item in candidates:
        if item["url"] in seen:
            continue

        seen.add(item["url"])
        unique.append(item)

    # The BoU page normally presents newer documents first.
    result = unique[0]

    print()
    print("Treasury Bond Invitation Found")
    print("----------------------------------------")
    print(f"Title: {result['title']}")
    print(f"Date:  {result['date'] or 'Not detected'}")
    print(f"PDF:   {result['url']}")
    print("----------------------------------------")

    return result


if __name__ == "__main__":
    find_latest_tender()