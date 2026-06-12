-- ══════════════════════════════════════════════════════════
-- Webvory Analytics — Materialized Views & Pre-Aggregation
-- Run once after data ingestion:
--   sudo -u postgres psql -d webvory_db -f database/views.sql
-- ══════════════════════════════════════════════════════════


-- ──────────────────────────────────────────────
-- 1. SUMMARY TABLE (pre-aggregated single-row metrics)
--    Holds: total orders, revenue, refunds, net revenue,
--    avg order value, repeat customer revenue
-- ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS analytics_summary (
    id                       SERIAL PRIMARY KEY,
    total_orders             BIGINT,
    total_revenue            NUMERIC(15,2),
    total_refunds            BIGINT,
    total_refund_amount      NUMERIC(15,2),
    net_revenue              NUMERIC(15,2),
    avg_order_value          NUMERIC(10,2),
    repeat_customer_revenue  NUMERIC(15,2),
    updated_at               TIMESTAMP DEFAULT NOW()
);

-- Initial population (refresh script will INSERT new rows periodically)
INSERT INTO analytics_summary (
    total_orders, total_revenue, total_refunds, total_refund_amount,
    net_revenue, avg_order_value, repeat_customer_revenue
)
SELECT
    (SELECT COUNT(*) FROM orders WHERE status = 'completed'),
    (SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'completed'),
    (SELECT COUNT(*) FROM refunds),
    (SELECT COALESCE(SUM(refund_amount), 0) FROM refunds),
    (SELECT COALESCE(SUM(amount), 0) FROM orders WHERE status = 'completed')
        - (SELECT COALESCE(SUM(refund_amount), 0) FROM refunds),
    (SELECT COALESCE(AVG(amount), 0) FROM orders WHERE status = 'completed'),
    (
        SELECT COALESCE(SUM(o.amount), 0)
        FROM orders o
        WHERE o.status = 'completed'
        AND o.customer_id IN (
            SELECT customer_id FROM orders
            WHERE status = 'completed'
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        )
    );


-- ──────────────────────────────────────────────
-- 2. MATERIALIZED VIEW: Revenue Trends (by month)
-- ──────────────────────────────────────────────

DROP MATERIALIZED VIEW IF EXISTS revenue_trends;

CREATE MATERIALIZED VIEW revenue_trends AS
SELECT
    DATE_TRUNC('month', order_date)::DATE AS month,
    COUNT(*)                              AS order_count,
    SUM(amount)                           AS revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Index on the view itself for fast sorting/filtering
CREATE UNIQUE INDEX IF NOT EXISTS idx_revenue_trends_month ON revenue_trends(month);


-- ──────────────────────────────────────────────
-- 3. MATERIALIZED VIEW: Top Customers by Spend
-- ──────────────────────────────────────────────

DROP MATERIALIZED VIEW IF EXISTS top_customers;

CREATE MATERIALIZED VIEW top_customers AS
SELECT
    o.customer_id,
    c.name,
    c.email,
    COUNT(*)        AS order_count,
    SUM(o.amount)   AS total_spend
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
GROUP BY o.customer_id, c.name, c.email
ORDER BY total_spend DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_top_customers_id ON top_customers(customer_id);
CREATE INDEX IF NOT EXISTS idx_top_customers_spend ON top_customers(total_spend DESC);


-- ══════════════════════════════════════════════════════════
-- Done. To refresh after new data ingestion, run:
--
--   REFRESH MATERIALIZED VIEW revenue_trends;
--   REFRESH MATERIALIZED VIEW top_customers;
--
-- (or use the Python refresh script which also updates
--  analytics_summary)
-- ══════════════════════════════════════════════════════════