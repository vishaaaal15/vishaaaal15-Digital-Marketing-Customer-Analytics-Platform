"""
generate_data.py
Generates a realistic synthetic dataset for the Digital Marketing & Customer
Analytics Platform project: 180,000 customers acquired across 12 campaigns
and 5 channels, with spend, conversion, and transaction-level revenue data
for cohort / RFM / CAC / CLV analysis.

This is SYNTHETIC data built to realistic, internally-consistent business
rules (not scraped or copied from any real company). It exists so every
metric in the README and resume is computed from real code output.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_CUSTOMERS = 180_000
CHANNELS = ["Paid Search", "Social Media", "Email", "Affiliate", "Display"]
CHANNEL_BASE_CAC = {"Paid Search": 280, "Social Media": 190, "Email": 60, "Affiliate": 220, "Display": 340}
CHANNEL_CONV_RATE = {"Paid Search": 0.052, "Social Media": 0.038, "Email": 0.091, "Affiliate": 0.044, "Display": 0.026}

CAMPAIGNS = [f"CMP-{i:02d}" for i in range(1, 13)]
# Guarantee every channel is represented at least once across the 12 campaigns
shuffled_channels = list(np.random.permutation(CHANNELS))
campaign_channel_map = {}
for idx, c in enumerate(CAMPAIGNS):
    if idx < len(shuffled_channels):
        campaign_channel_map[c] = shuffled_channels[idx]
    else:
        campaign_channel_map[c] = np.random.choice(CHANNELS)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=np.random.randint(0, delta.days))

rows = []
for i in range(N_CUSTOMERS):
    campaign = np.random.choice(CAMPAIGNS)
    channel = campaign_channel_map[campaign]
    acq_date = random_date(START_DATE, END_DATE)
    converted = np.random.rand() < CHANNEL_CONV_RATE[channel]
    spend = np.random.gamma(shape=2.0, scale=CHANNEL_BASE_CAC[channel] / 2)

    rows.append({
        "customer_id": f"CUST-{i:07d}",
        "campaign_id": campaign,
        "channel": channel,
        "acquisition_date": acq_date.date().isoformat(),
        "ad_spend": round(spend, 2),
        "converted": int(converted),
    })

customers = pd.DataFrame(rows)
customers.to_csv("/home/claude/digital-marketing-project/data/customers.csv", index=False)

# Transactions for converted customers (repeat purchase behavior for CLV/RFM/cohort)
txn_rows = []
converted_customers = customers[customers["converted"] == 1]

for _, c in converted_customers.iterrows():
    acq = datetime.fromisoformat(c["acquisition_date"])
    n_orders = np.random.poisson(2.3) + 1  # at least 1 order
    last_date = acq
    for order_num in range(n_orders):
        gap_days = np.random.randint(1, 75)
        order_date = last_date + timedelta(days=gap_days)
        if order_date > END_DATE + timedelta(days=60):
            break
        order_value = max(150, np.random.normal(1450, 600))
        txn_rows.append({
            "customer_id": c["customer_id"],
            "order_date": order_date.date().isoformat(),
            "order_value": round(order_value, 2),
        })
        last_date = order_date

transactions = pd.DataFrame(txn_rows)
transactions.to_csv("/home/claude/digital-marketing-project/data/transactions.csv", index=False)

print(f"customers.csv     -> {len(customers):,} rows")
print(f"transactions.csv  -> {len(transactions):,} rows")
print(f"Total ad spend    -> Rs. {customers['ad_spend'].sum():,.0f}")
print(f"Total conversions -> {customers['converted'].sum():,} ({customers['converted'].mean()*100:.2f}% overall conv. rate)")
