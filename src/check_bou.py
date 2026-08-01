from playwright.sync_api import sync_playwright

URL = "https://bou.or.ug/financial-markets/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    print("Opening BoU website...")

    page.goto(URL, wait_until="networkidle")

    print("Page loaded")

    print("Title:")
    print(page.title())

    print()

    print("Looking for Invitation to Tender...")

    links = page.locator("a").all()

    print(f"Found {len(links)} links")

    for link in links:
        try:
            text = link.inner_text().strip()
            href = link.get_attribute("href")

            if text:
                print(text)

            if href:
                print(href)

            print("-" * 40)

        except Exception:
            pass

    browser.close()