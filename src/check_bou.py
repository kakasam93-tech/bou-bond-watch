import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://bou.or.ug/financial-markets/"

print("Checking Bank of Uganda Financial Markets page...")

response = requests.get(URL, timeout=30)
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

found = False

for link in soup.find_all("a", href=True):
    href = link["href"]
    text = link.get_text(" ", strip=True)

    if ".pdf" in href.lower():
        full_url = urljoin(URL, href)
        print(f"PDF: {text}")
        print(full_url)
        print("-" * 50)
        found = True

if not found:
    print("No PDF links found.")
print("\n========== PAGE TITLE ==========")
print(soup.title.string if soup.title else "No title")

print("\n========== FIRST 30 LINKS ==========")

links = soup.find_all("a", href=True)

print(f"Total links found: {len(links)}")

for i, link in enumerate(links[:30], start=1):
    text = link.get_text(" ", strip=True)
    href = link["href"]
    print(f"{i}. {text}")
    print(f"   {href}")
