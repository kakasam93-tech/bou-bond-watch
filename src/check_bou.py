from detector import find_latest_bond


def main():
    print("=" * 60)
    print("BoU Bond Watch")
    print("=" * 60)

    print("Checking official Bank of Uganda Financial Markets page...")
    print()

    tender = find_latest_bond()

    if tender is None:
        print()
        print("No Treasury Bond Invitation to Tender found.")
        return

    print()
    print("=" * 60)
    print("LATEST TREASURY BOND TENDER")
    print("=" * 60)
    print(f"Title: {tender.title}")
    print(f"PDF: {tender.pdf_url}")
    print()
    print("Treasury bond detected.")


if __name__ == "__main__":
    main()