from dataclasses import dataclass

@dataclass
class BondTender:
    title: str
    pdf_url: str
    publication_date: str = ""