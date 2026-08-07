"""
Bank of Uganda Treasury Bond detector.

Purpose:
    Find the latest genuine Bank of Uganda Treasury Bond
    Invitation to Tender / Scheduled Auction.

Important:
    Treasury Bills are explicitly excluded.

The detector:
    - Scrapes the official BoU Financial Markets page
    - Handles PDF links
    - Recognises multiple BoU naming conventions
    - Extracts the AUCTION DATE where possible
    - Scores candidates instead of relying on one exact phrase
    - Sorts candidates by auction date
    - Returns the newest genuine Treasury Bond tender
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

BOU_FINANCIAL_MARKETS_URL = (
    "https://bou.or.ug/bouwebsite/FinancialMarkets/"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# TERMS
# ---------------------------------------------------------------------------

# Strong Treasury Bond indicators.
BOND_TERMS = [
    "treasury bond",
    "treasury bonds",
    "government treasury bond",
    "government treasury bonds",
    "uganda government treasury bond",
    "uganda government treasury bonds",
    "government bond",
    "government bonds",
    "government securities",
    "treasury bond auction",
    "treasury bond tender",
    "treasury bonds auction",
    "treasury bonds tender",
]


# Terms strongly associated with an actual auction/tender notice.
TENDER_TERMS = [
    "invitation to tender",
    "invitation to tenders",
    "invitation to bid",
    "scheduled auction",
    "auction date",
    "auction",
    "tender",
    "tenders",
    "primary auction",
    "re-opening",
    "reopen",
    "re-open",
]


# Treasury Bills must NEVER be accepted.
EXCLUDE_TERMS = [
    "treasury bill",
    "treasury bills",
    "t-bill",
    "t-bills",
]


# Words that can occur on general BoU pages but are not enough
# by themselves to identify an actual bond tender.
WEAK_TERMS = [
    "financial markets",
    "government securities",
    "securities",
]


# ---------------------------------------------------------------------------
# TEXT HELPERS
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Normalize text for reliable keyword matching.
    """
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    return text.lower().strip()


def contains_any(text: str, terms: list[str]) -> bool:
    """
    Return True if any term occurs in text.
    """
    return any(term in text for term in terms)


def is_pdf_url(url: str) -> bool:
    """
    Determine whether a URL points to a PDF.
    """
    path = urlparse(url).path.lower()
    return path.endswith(".pdf")


# ---------------------------------------------------------------------------
# DATE PARSING
# ---------------------------------------------------------------------------

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_date_string(value: str) -> Optional[datetime]:
    """
    Try several date formats commonly encountered on BoU documents.
    """

    if not value:
        return None

    value = value.strip()

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d-%B-%Y",
        "%d-%b-%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return None


def extract_auction_date(text: str) -> Optional[datetime]:
    """
    Extract the date associated specifically with AUCTION DATE.

    This is much safer than simply finding the first date in a document,
    because Treasury Bond PDFs contain many coupon-payment dates.
    """

    if not text:
        return None

    # Normalize whitespace but preserve punctuation.
    cleaned = re.sub(r"\s+", " ", text)

    # Look specifically around "auction date".
    auction_patterns = [
        # AUCTION DATE: Wednesday July 01, 2026
        r"auction\s+date\s*[:\-]?\s*"
        r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)?"
        r"\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})",

        # AUCTION DATE: 01 July 2026
        r"auction\s+date\s*[:\-]?\s*"
        r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)?"
        r"\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})",

        # AUCTION DATE: July 01, 2026
        r"auction\s+date\s*[:\-]?\s*"
        r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)?"
        r"\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})",

        # AUCTION DATE: 01/07/2026
        r"auction\s+date\s*[:\-]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",

        # AUCTION DATE: 2026-07-01
        r"auction\s+date\s*[:\-]?\s*"
        r"(\d{4}-\d{1,2}-\d{1,2})",
    ]

    for pattern in auction_patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)

        if match:
            value = match.group(1).strip()

            # Remove accidental punctuation.
            value = value.rstrip(".,;")

            parsed = parse_date_string(value)

            if parsed:
                return parsed

    # ------------------------------------------------------------------
    # Fallback: search for common dates, but ONLY if the surrounding
    # text strongly suggests this is an auction notice.
    # ------------------------------------------------------------------

    date_patterns = [
        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}\b",
        r"\b[A-Za-z]+\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b",
        r"\b\d{4}-\d{1,2}-\d{1,2}\b",
    ]

    for pattern in date_patterns:
        for match in re.finditer(pattern, cleaned):
            candidate = match.group(0)
            parsed = parse_date_string(candidate)

            if not parsed:
                continue

            # Only accept the fallback date if "auction" occurs nearby.
            start = max(0, match.start() - 100)
            end = min(len(cleaned), match.end() + 100)

            context = cleaned[start:end]

            if "auction" in context:
                return parsed

    return None


# Backward-compatible function name.
def extract_date(text: str) -> Optional[str]:
    """
    Return the auction date as text.

    Kept for compatibility with the previous detector.py.
    """
    parsed = extract_auction_date(text)

    if parsed:
        return parsed.strftime("%d %B %Y")

    return None


# ---------------------------------------------------------------------------
# DOCUMENT VALIDATION
# ---------------------------------------------------------------------------

def is_treasury_bond_tender(title: str, url: str, document_text: str = "") -> bool:
    """
    Determine whether a document is a genuine Treasury Bond
    Invitation to Tender / Scheduled Auction.

    Treasury Bills are explicitly rejected.
    """

    combined = normalize(
        f"{title} {url} {document_text}"
    )

    # ---------------------------------------------------------------
    # 1. Treasury Bills are NEVER accepted.
    # ---------------------------------------------------------------

    if contains_any(combined, EXCLUDE_TERMS):
        return False

    # ---------------------------------------------------------------
    # 2. Must contain Treasury Bond language.
    # ---------------------------------------------------------------

    has_bond = contains_any(combined, BOND_TERMS)

    if not has_bond:
        return False

    # ---------------------------------------------------------------
    # 3. Must look like an actual auction/tender.
    # ---------------------------------------------------------------

    has_tender = contains_any(combined, TENDER_TERMS)

    if not has_tender:
        return False

    # ---------------------------------------------------------------
    # 4. Strong BoU tender documents normally contain at least one
    #    of these fields.
    # ---------------------------------------------------------------

    strong_document_terms = [
        "auction date",
        "settlement date",
        "offering amount",
        "minimum competitive bid",
        "non competitive bid",
        "non-competitive bid",
        "submission of bids",
        "pricing and submission of bids",
    ]

    has_strong_document_structure = contains_any(
        combined,
        strong_document_terms,
    )

    # If this is a PDF or explicit tender link, bond+tender is usually
    # sufficient. For ordinary HTML links, demand stronger evidence.
    if not has_strong_document_structure:
        if not is_pdf_url(url):
            return False

    return True


# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------

def score_candidate(
    title: str,
    url: str,
    document_text: str = "",
) -> int:
    """
    Score a candidate.

    Higher = more likely to be an actual Treasury Bond
    Invitation to Tender.
    """

    combined = normalize(
        f"{title} {url} {document_text}"
    )

    score = 0

    # Strongest indicators.
    if "invitation to tender" in combined:
        score += 40

    if "scheduled auction" in combined:
        score += 35

    if "auction date" in combined:
        score += 30

    if "uganda government treasury bond" in combined:
        score += 30

    if "treasury bond" in combined:
        score += 25

    if "treasury bonds" in combined:
        score += 25

    if "government treasury bond" in combined:
        score += 25

    if "settlement date" in combined:
        score += 15

    if "offering amount" in combined:
        score += 15

    if "submission of bids" in combined:
        score += 15

    if "minimum competitive bid" in combined:
        score += 10

    if "pricing and submission of bids" in combined:
        score += 10

    if "re-opening" in combined or "re-open" in combined:
        score += 5

    if is_pdf_url(url):
        score += 10

    # Treasury Bill penalty.
    if contains_any(combined, EXCLUDE_TERMS):
        score -= 1000

    return score


# ---------------------------------------------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------------------------------------------

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF.

    Uses pypdf when available.

    If extraction fails, returns an empty string rather than crashing
    the entire scraper.
    """

    try:
        from io import BytesIO
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(pdf_bytes))

        pages = []

        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                continue

        return "\n".join(pages)

    except Exception as exc:
        print(f"PDF text extraction unavailable/failed: {exc}")
        return ""


# ---------------------------------------------------------------------------
# DOWNLOAD DOCUMENT
# ---------------------------------------------------------------------------

def fetch_document_text(url: str) -> str:
    """
    Download a PDF/HTML document and return useful text.

    This is deliberately defensive so that one bad link doesn't
    terminate the entire GitHub Actions job.
    """

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"Unable to fetch document {url}: {exc}")
        return ""

    content_type = normalize(
        response.headers.get("Content-Type", "")
    )

    if is_pdf_url(url) or "application/pdf" in content_type:
        return extract_pdf_text(response.content)

    try:
        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        return soup.get_text(" ", strip=True)

    except Exception:
        return response.text


# ---------------------------------------------------------------------------
# CANDIDATE EXTRACTION
# ---------------------------------------------------------------------------

def collect_candidates(soup: BeautifulSoup) -> list[dict]:
    """
    Inspect all links on the BoU Financial Markets page.
    """

    candidates = []

    links = soup.find_all("a", href=True)

    print(f"Found {len(links)} links on BoU Financial Markets page.")

    for index, link in enumerate(links, start=1):

        title = link.get_text(" ", strip=True)

        href = link.get("href", "").strip()

        if not href:
            continue

        url = urljoin(
            BOU_FINANCIAL_MARKETS_URL,
            href,
        )

        # Combine visible title + URL first.
        initial_text = normalize(
            f"{title} {url}"
        )

        # -----------------------------------------------------------
        # Quick rejection of Treasury Bills.
        # -----------------------------------------------------------

        if contains_any(initial_text, EXCLUDE_TERMS):
            continue

        # -----------------------------------------------------------
        # Only investigate links that have some bond/tender signal.
        # This avoids downloading every PDF on the page.
        # -----------------------------------------------------------

        possible = (
            contains_any(initial_text, BOND_TERMS)
            or contains_any(initial_text, TENDER_TERMS)
            or is_pdf_url(url)
        )

        if not possible:
            continue

        print()
        print(f"Checking candidate #{index}")
        print(f"Title: {title}")
        print(f"URL:   {url}")

        # -----------------------------------------------------------
        # Download the document when it is a PDF or looks promising.
        # -----------------------------------------------------------

        document_text = ""

        if is_pdf_url(url):
            document_text = fetch_document_text(url)

        # -----------------------------------------------------------
        # Validate.
        # -----------------------------------------------------------

        if not is_treasury_bond_tender(
            title,
            url,
            document_text,
        ):
            print("Rejected: not a Treasury Bond tender.")
            continue

        combined = normalize(
            f"{title} {url} {document_text}"
        )

        auction_date = extract_auction_date(
            document_text
        )

        # If PDF text didn't provide the date, try title + URL.
        if auction_date is None:
            auction_date = extract_auction_date(
                f"{title} {url}"
            )

        score = score_candidate(
            title,
            url,
            document_text,
        )

        candidate = {
            "title": (
                title
                or "Treasury Bond Invitation to Tender"
            ),
            "url": url,
            "date": (
                auction_date.strftime("%d %B %Y")
                if auction_date
                else None
            ),
            "auction_date": auction_date,
            "score": score,
            "text": document_text,
        }

        candidates.append(candidate)

        print(
            f"Accepted candidate: "
            f"score={score}, "
            f"auction_date={candidate['date']}"
        )

    return candidates


# ---------------------------------------------------------------------------
# FIND LATEST TENDER
# ---------------------------------------------------------------------------

def find_latest_tender() -> Optional[dict]:
    """
    Search the official Bank of Uganda Financial Markets page
    and return the latest genuine Treasury Bond auction/tender.
    """

    print()
    print("=" * 70)
    print("BoU Treasury Bond Watch")
    print("=" * 70)
    print()
    print(
        "Checking official Bank of Uganda Financial Markets page..."
    )
    print(BOU_FINANCIAL_MARKETS_URL)
    print()

    try:
        response = requests.get(
            BOU_FINANCIAL_MARKETS_URL,
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        print(
            "Unable to access Bank of Uganda website: "
            f"{exc}"
        )
        return None

    print(
        f"BoU page loaded successfully "
        f"(HTTP {response.status_code})."
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    candidates = collect_candidates(soup)

    if not candidates:
        print()
        print(
            "No Treasury Bond Invitation to Tender found."
        )
        return None

    # ---------------------------------------------------------------
    # Sort by:
    #
    # 1. Auction date, newest first
    # 2. Score, strongest first
    #
    # Candidates without a date are placed after dated candidates.
    # ---------------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            item["auction_date"] is not None,
            item["auction_date"] or datetime.min,
            item["score"],
        ),
        reverse=True,
    )

    result = candidates[0]

    print()
    print("=" * 70)
    print("LATEST TREASURY BOND INVITATION FOUND")
    print("=" * 70)

    print(
        f"Title: {result['title']}"
    )

    print(
        f"Auction Date: "
        f"{result['date'] or 'Not detected'}"
    )

    print(
        f"Score: {result['score']}"
    )

    print(
        f"PDF/URL: {result['url']}"
    )

    print("=" * 70)

    # ---------------------------------------------------------------
    # Show other candidates for debugging.
    # ---------------------------------------------------------------

    if len(candidates) > 1:
        print()
        print("Other Treasury Bond candidates:")

        for item in candidates[1:]:
            print(
                f"- {item['date'] or 'No date'} | "
                f"{item['score']} | "
                f"{item['title']} | "
                f"{item['url']}"
            )

    return result


# ---------------------------------------------------------------------------
# BACKWARD COMPATIBILITY
# ---------------------------------------------------------------------------

def find_latest_bond():
    """
    Backward-compatible function name used by check_bou.py.
    """

    return find_latest_tender()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    find_latest_tender()