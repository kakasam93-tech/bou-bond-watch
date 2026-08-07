from dataclasses import dataclass


@dataclass
class BondTender:
    """
    Represents a Treasury Bond Invitation to Tender
    discovered on the Bank of Uganda website.
    """

    title: str
    pdf_url: str
    publication_date: str = ""
