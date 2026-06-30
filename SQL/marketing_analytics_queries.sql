-- ============================================================
-- Digital Marketing & Customer Analytics Platform
-- SQL Query Library (14 queries)
-- Schema: customers(customer_id, campaign_id, channel, acquisition_date,
--                    ad_spend, converted)
--         transactions(customer_id, order_date, order_value)
-- Tested against SQLite (see python/run_sql_queries.py)
-- ============================================================

-- 1. Total ad spend and conversions by channel
SELECT
    channel,
    COUNT(*)                                  AS customers_targeted,
    SUM(converted)                            AS conversions,
    ROUND(SUM(converted) * 100.0 / COUNT(*),2) AS conversion_rate_pct,
    ROUND(SUM(ad_spend), 2)                   AS total_ad_spend
FROM customers
GROUP BY channel
ORDER BY total_ad_spend DESC;

-- 2. Customer Acquisition Cost (CAC) by channel
SELECT
    channel,
    ROUND(SUM(ad_spend), 2)                          AS total_spend,
    SUM(converted)                                   AS conversions,
    ROUND(SUM(ad_spend) * 1.0 / NULLIF(SUM(converted),0), 2) AS cac
FROM customers
GROUP BY channel
ORDER BY cac ASC;

-- 3. CAC by campaign
SELECT
    campaign_id,
    channel,
    ROUND(SUM(ad_spend), 2) AS total_spend,
    SUM(converted)          AS conversions,
    ROUND(SUM(ad_spend) * 1.0 / NULLIF(SUM(converted),0), 2) AS cac
FROM customers
GROUP BY campaign_id, channel
ORDER BY cac ASC;

-- 4. Conversion funnel drop-off by channel (targeted -> converted)
SELECT
    channel,
    COUNT(*)                                   AS targeted,
    SUM(converted)                             AS converted,
    COUNT(*) - SUM(converted)                  AS dropped_off,
    ROUND((COUNT(*) - SUM(converted)) * 100.0 / COUNT(*), 2) AS dropoff_rate_pct
FROM customers
GROUP BY channel
ORDER BY dropoff_rate_pct DESC;

-- 5. Total revenue and order count per customer
SELECT
    customer_id,
    COUNT(*)            AS order_count,
    ROUND(SUM(order_value), 2) AS total_revenue
FROM transactions
GROUP BY customer_id;

-- 6. Customer Lifetime Value (CLV) by acquisition channel
SELECT
    c.channel,
    COUNT(DISTINCT c.customer_id)                              AS converted_customers,
    ROUND(SUM(t.order_value), 2)                                AS total_revenue,
    ROUND(SUM(t.order_value) * 1.0 / COUNT(DISTINCT c.customer_id), 2) AS avg_clv
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.channel
ORDER BY avg_clv DESC;

-- 7. Channel ROI (revenue generated per rupee of ad spend)
SELECT
    c.channel,
    ROUND(SUM(c.ad_spend), 2)                                     AS total_spend,
    ROUND(SUM(t.revenue), 2)                                      AS total_revenue,
    ROUND((SUM(t.revenue) - SUM(c.ad_spend)) * 100.0 / SUM(c.ad_spend), 2) AS roi_pct
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(order_value) AS revenue
    FROM transactions
    GROUP BY customer_id
) t ON c.customer_id = t.customer_id
GROUP BY c.channel
ORDER BY roi_pct DESC;

-- 8. Average order value (AOV) overall and by channel
SELECT
    c.channel,
    ROUND(AVG(t.order_value), 2) AS avg_order_value
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.channel
ORDER BY avg_order_value DESC;

-- 9. RFM base table: Recency, Frequency, Monetary per customer
-- (reference date hardcoded for snapshot reproducibility)
SELECT
    customer_id,
    JULIANDAY('2026-01-15') - JULIANDAY(MAX(order_date)) AS recency_days,
    COUNT(*)                                              AS frequency,
    ROUND(SUM(order_value), 2)                            AS monetary
FROM transactions
GROUP BY customer_id;

-- 10. Top 10% customers by monetary value (high-value segment)
SELECT customer_id, total_revenue
FROM (
    SELECT customer_id, SUM(order_value) AS total_revenue
    FROM transactions
    GROUP BY customer_id
)
ORDER BY total_revenue DESC
LIMIT (SELECT CAST(COUNT(DISTINCT customer_id) * 0.10 AS INT) FROM transactions);

-- 11. Monthly new-customer acquisition trend
SELECT
    SUBSTR(acquisition_date, 1, 7) AS acquisition_month,
    COUNT(*)                       AS new_customers,
    SUM(converted)                 AS conversions
FROM customers
GROUP BY acquisition_month
ORDER BY acquisition_month;

-- 12. Cohort retention: % of customers with a repeat order within 60 days
SELECT
    c.customer_id,
    MIN(t.order_date)                                         AS first_order,
    COUNT(t.order_date)                                       AS total_orders,
    CASE WHEN COUNT(t.order_date) > 1 THEN 1 ELSE 0 END       AS repeat_purchaser
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id;

-- 13. Campaign efficiency ranking (spend vs revenue generated)
SELECT
    c.campaign_id,
    c.channel,
    ROUND(SUM(c.ad_spend), 2)        AS total_spend,
    ROUND(SUM(t.revenue), 2)         AS total_revenue,
    ROUND(SUM(t.revenue) - SUM(c.ad_spend), 2) AS net_value
FROM customers c
LEFT JOIN (
    SELECT customer_id, SUM(order_value) AS revenue
    FROM transactions
    GROUP BY customer_id
) t ON c.customer_id = t.customer_id
GROUP BY c.campaign_id, c.channel
ORDER BY net_value DESC;

-- 14. Underperforming campaigns flagged for review (CAC above overall average)
SELECT
    campaign_id,
    channel,
    ROUND(SUM(ad_spend) * 1.0 / NULLIF(SUM(converted),0), 2) AS cac
FROM customers
GROUP BY campaign_id, channel
HAVING cac > (SELECT SUM(ad_spend) * 1.0 / NULLIF(SUM(converted),0) FROM customers)
ORDER BY cac DESC;
