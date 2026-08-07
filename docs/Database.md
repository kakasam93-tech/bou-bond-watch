# Database Design

## Bond Master

One record per ISIN.

Fields

- ISIN
- Security
- Coupon
- Tenor
- Original Issue Date
- Maturity
- Coupon Frequency
- Coupon Months
- Status

---

## Auction History

One record per auction.

Fields

- Auction Date
- Settlement Date
- Amount Offered
- Amount Applied
- Amount Accepted
- Average Yield
- Cut-off Yield
- Tender PDF
- Results PDF

---

## Portfolio

Personal investments.

Fields

- ISIN
- Purchase Date
- Amount
- Yield
- Next Coupon
- Status