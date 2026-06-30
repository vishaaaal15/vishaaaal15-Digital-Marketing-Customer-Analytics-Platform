"""
analysis.py
Loads the synthetic dataset into SQLite, runs the SQL query library,
performs RFM segmentation and cohort analysis in pandas, and generates
the dashboard-ready charts and the summary metrics used in the README.
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/claude/digital-marketing-project"

# ---------------------------------------------------------------
# 1. Load data into SQLite
# ---------------------------------------------------------------
customers = pd.read_csv(f"{BASE}/data/customers.csv")
transactions = pd.read_csv(f"{BASE}/data/transactions.csv")

conn = sqlite3.connect(":memory:")
customers.to_sql("customers", conn, index=False)
transactions.to_sql("transactions", conn, index=False)

# ---------------------------------------------------------------
# 2. Core KPIs
# ---------------------------------------------------------------
total_spend = customers["ad_spend"].sum()
total_customers = len(customers)
total_conversions = customers["converted"].sum()
overall_conv_rate = total_conversions / total_customers * 100
overall_cac = total_spend / total_conversions

revenue_by_cust = transactions.groupby("customer_id")["order_value"].sum()
total_revenue = revenue_by_cust.sum()
avg_clv = revenue_by_cust.mean()

print("=== CORE KPIs ===")
print(f"Customers targeted:     {total_customers:,}")
print(f"Total ad spend:         Rs. {total_spend:,.0f}")
print(f"Conversions:            {total_conversions:,}")
print(f"Overall conversion rate:{overall_conv_rate:.2f}%")
print(f"Overall CAC:            Rs. {overall_cac:,.2f}")
print(f"Total revenue:          Rs. {total_revenue:,.0f}")
print(f"Average CLV:            Rs. {avg_clv:,.2f}")
print(f"Overall ROI:            {(total_revenue-total_spend)/total_spend*100:.2f}%")

# ---------------------------------------------------------------
# 3. CAC & ROI by channel
# ---------------------------------------------------------------
cac_by_channel = pd.read_sql("""
    SELECT channel,
           ROUND(SUM(ad_spend),2) AS total_spend,
           SUM(converted) AS conversions,
           ROUND(SUM(ad_spend)*1.0/NULLIF(SUM(converted),0),2) AS cac
    FROM customers GROUP BY channel ORDER BY cac ASC
""", conn)
print("\n=== CAC by Channel ===")
print(cac_by_channel.to_string(index=False))

roi_query = """
SELECT c.channel,
       ROUND(SUM(c.ad_spend),2) AS total_spend,
       ROUND(SUM(COALESCE(t.revenue,0)),2) AS total_revenue
FROM customers c
LEFT JOIN (SELECT customer_id, SUM(order_value) AS revenue FROM transactions GROUP BY customer_id) t
  ON c.customer_id = t.customer_id
GROUP BY c.channel
"""
roi_by_channel = pd.read_sql(roi_query, conn)
roi_by_channel["roi_pct"] = ((roi_by_channel["total_revenue"] - roi_by_channel["total_spend"])
                              / roi_by_channel["total_spend"] * 100).round(2)
roi_by_channel = roi_by_channel.sort_values("roi_pct", ascending=False)
print("\n=== ROI by Channel ===")
print(roi_by_channel.to_string(index=False))

# ---------------------------------------------------------------
# 4. RFM Segmentation
# ---------------------------------------------------------------
snapshot_date = pd.to_datetime("2026-01-15")
transactions["order_date"] = pd.to_datetime(transactions["order_date"])

rfm = transactions.groupby("customer_id").agg(
    recency_days=("order_date", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_date", "count"),
    monetary=("order_value", "sum")
).reset_index()

rfm["R_score"] = pd.qcut(rfm["recency_days"], 4, labels=[4,3,2,1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
rfm["M_score"] = pd.qcut(rfm["monetary"], 4, labels=[1,2,3,4]).astype(int)
rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

def segment(row):
    if row["RFM_score"] >= 10:
        return "High-Value"
    elif row["RFM_score"] >= 7:
        return "Mid-Value"
    else:
        return "Low-Value"

rfm["segment"] = rfm.apply(segment, axis=1)
seg_summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"),
    total_revenue=("monetary", "sum")
).reset_index()
seg_summary["pct_of_customers"] = (seg_summary["customers"] / seg_summary["customers"].sum() * 100).round(2)
seg_summary["pct_of_revenue"] = (seg_summary["total_revenue"] / seg_summary["total_revenue"].sum() * 100).round(2)

print("\n=== RFM Segment Summary ===")
print(seg_summary.to_string(index=False))

high_value_row = seg_summary[seg_summary["segment"] == "High-Value"].iloc[0]
print(f"\nKey insight: High-Value segment = {high_value_row['pct_of_customers']}% of customers, "
      f"generating {high_value_row['pct_of_revenue']}% of revenue.")

rfm.to_csv(f"{BASE}/outputs/rfm_segments.csv", index=False)

# ---------------------------------------------------------------
# 5. Cohort / repeat purchase analysis
# ---------------------------------------------------------------
order_counts = transactions.groupby("customer_id")["order_date"].count()
repeat_rate = (order_counts > 1).mean() * 100
print(f"\nRepeat purchase rate (2+ orders): {repeat_rate:.2f}%")

# ---------------------------------------------------------------
# 6. Charts for dashboard
# ---------------------------------------------------------------
plt.figure(figsize=(7,4))
plt.bar(cac_by_channel["channel"], cac_by_channel["cac"], color="#2E5395")
plt.title("Customer Acquisition Cost (CAC) by Channel")
plt.ylabel("CAC (Rs.)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(f"{BASE}/outputs/cac_by_channel.png", dpi=130)
plt.close()

plt.figure(figsize=(7,4))
colors = ["#2E5395" if v >= 0 else "#C0392B" for v in roi_by_channel["roi_pct"]]
plt.bar(roi_by_channel["channel"], roi_by_channel["roi_pct"], color=colors)
plt.title("ROI by Channel (%)")
plt.ylabel("ROI %")
plt.axhline(0, color="black", linewidth=0.8)
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig(f"{BASE}/outputs/roi_by_channel.png", dpi=130)
plt.close()

plt.figure(figsize=(6,5))
plt.pie(seg_summary["customers"], labels=seg_summary["segment"], autopct="%1.1f%%",
        colors=["#1F3864","#2E5395","#A9C2E0"])
plt.title("Customer Segments by RFM (% of customers)")
plt.tight_layout()
plt.savefig(f"{BASE}/outputs/rfm_segments_pie.png", dpi=130)
plt.close()

monthly = pd.read_sql("""
    SELECT SUBSTR(acquisition_date,1,7) AS month, COUNT(*) AS new_customers, SUM(converted) AS conversions
    FROM customers GROUP BY month ORDER BY month
""", conn)
plt.figure(figsize=(8,4))
plt.plot(monthly["month"], monthly["new_customers"], marker="o", label="New Customers", color="#2E5395")
plt.plot(monthly["month"], monthly["conversions"], marker="o", label="Conversions", color="#C0392B")
plt.title("Monthly Acquisition Trend")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(f"{BASE}/outputs/monthly_trend.png", dpi=130)
plt.close()

print("\nCharts saved to outputs/: cac_by_channel.png, roi_by_channel.png, rfm_segments_pie.png, monthly_trend.png")

# ---------------------------------------------------------------
# 7. Save summary metrics for README
# ---------------------------------------------------------------
summary = {
    "total_customers": int(total_customers),
    "total_ad_spend": round(total_spend, 2),
    "total_conversions": int(total_conversions),
    "overall_conversion_rate_pct": round(overall_conv_rate, 2),
    "overall_cac": round(overall_cac, 2),
    "total_revenue": round(total_revenue, 2),
    "overall_roi_pct": round((total_revenue - total_spend) / total_spend * 100, 2),
    "avg_clv": round(avg_clv, 2),
    "repeat_purchase_rate_pct": round(repeat_rate, 2),
    "high_value_pct_of_customers": float(high_value_row["pct_of_customers"]),
    "high_value_pct_of_revenue": float(high_value_row["pct_of_revenue"]),
    "best_channel_by_roi": roi_by_channel.iloc[0]["channel"],
    "best_channel_roi_pct": float(roi_by_channel.iloc[0]["roi_pct"]),
    "lowest_cac_channel": cac_by_channel.iloc[0]["channel"],
    "lowest_cac_value": float(cac_by_channel.iloc[0]["cac"]),
}

import json
with open(f"{BASE}/outputs/summary_metrics.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\nSummary metrics saved to outputs/summary_metrics.json")
