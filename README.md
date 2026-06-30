# Digital Marketing & Customer Analytics Platform

End-to-end marketing analytics project analyzing customer acquisition, channel performance, and customer value across a simulated 180,000-customer dataset spanning 12 campaigns and 5 digital channels. Built with SQL, Python, and dashboard visualizations to surface acquisition efficiency, ROI, and high-value customer segments for data-driven budget allocation.

## Tech Stack
SQL (SQLite) · Python (Pandas, NumPy, Matplotlib) · RFM Segmentation · Cohort Analysis · Power BI / Tableau-style Dashboard

## Dataset
- **180,000 customers** acquired across **12 campaigns** and **5 channels**: Email, Social Media, Affiliate, Paid Search, Display
- **27,706 transactions** from converted customers (repeat purchase behavior modeled for CLV/RFM analysis)
- Data is synthetically generated (`python/generate_data.py`) using realistic, channel-specific conversion rates and spend distributions — built to demonstrate the analytical pipeline end-to-end, not scraped or sourced from a real company.

## Methodology
1. **Data generation** — synthetic customer and transaction data with channel-specific CAC and conversion-rate assumptions (`python/generate_data.py`)
2. **SQL analysis** — 14 queries covering CAC, ROI, conversion funnel, RFM base tables, cohort retention, and campaign efficiency ranking (`sql/marketing_analytics_queries.sql`)
3. **Python analysis** — RFM segmentation (Recency, Frequency, Monetary scoring), repeat-purchase/cohort analysis, and channel-level CAC/ROI computation (`python/analysis.py`)
4. **Dashboard** — channel performance and segment visualizations (`dashboard/`)

## Key Findings (from actual script output — see `outputs/summary_metrics.json`)

| Metric | Value |
|---|---|
| Total ad spend analyzed | ₹3.72 Cr (₹37.19M) |
| Customers targeted | 180,000 |
| Conversions | 9,505 (5.28% conversion rate) |
| Overall CAC | ₹3,912.56 |
| Total revenue generated | ₹4.03 Cr (₹40.35M) |
| Overall ROI | 8.50% |
| Average CLV | ₹4,263.88 |
| Repeat purchase rate | 85.23% |
| High-value segment | 25.8% of customers generate 41.63% of revenue |
| Most efficient channel | Email — lowest CAC (₹659) and highest ROI (540.66%) |
| Least efficient channel | Display — highest CAC (₹13,227), ROI -67.6% |

**Business takeaway:** Email is by far the most cost-efficient acquisition channel (CAC ~20x lower than Display), while Display spend is actively destroying value at current conversion rates. Reallocating budget from Display toward Email and Affiliate, combined with retention-focused campaigns for the High-Value RFM segment (41.6% of revenue from a quarter of customers), is the clearest lever for improving overall marketing ROI.

## Repository Structure
```
digital-marketing-customer-analytics-platform/
├── data/
│   ├── customers.csv
│   └── transactions.csv
├── sql/
│   └── marketing_analytics_queries.sql      (14 queries)
├── python/
│   ├── generate_data.py
│   └── analysis.py                          (RFM, cohort, CAC/ROI, charts)
├── outputs/
│   ├── summary_metrics.json
│   ├── rfm_segments.csv
│   ├── cac_by_channel.png
│   ├── roi_by_channel.png
│   ├── rfm_segments_pie.png
│   └── monthly_trend.png
├── dashboard/
│   └── dashboard.html                       (interactive summary dashboard)
└── README.md
```

## How to Run
```bash
pip install pandas numpy matplotlib
python python/generate_data.py     # generates data/customers.csv, data/transactions.csv
python python/analysis.py          # runs SQL + RFM + cohort analysis, saves charts to outputs/
```
Open `dashboard/dashboard.html` in a browser to view the summary dashboard.

## Author
Vishal Singh — [GitHub](https://github.com/vishaaaal15) · [LinkedIn](https://www.linkedin.com/in/vishal-singhdataanalyst)
