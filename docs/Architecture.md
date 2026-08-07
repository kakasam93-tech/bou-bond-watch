 # BoU Bond Watch Architecture

## Objective

Automatically monitor the Bank of Uganda website for new Treasury Bond Invitations to Tender.

## Workflow

GitHub Actions
    ↓
Detector
    ↓
Download PDF
    ↓
Validate
    ↓
Parse PDF
    ↓
Store Data
    ↓
Notify User

## Components

- detector.py
- downloader.py
- validator.py
- pdf_parser.py
- storage.py
- notifier.py
- analytics.py
- portfolio.py