SET search_path TO ecommerce, public;

-- One row per calendar month, including months with zero sales.
WITH calendar AS (
    SELECT generate_series(
        date_trunc('month', (SELECT MIN(order_date) FROM orders)),
        date_trunc('month', (SELECT MAX(order_date) FROM orders)), '1 month'
    )::date AS month
), monthly AS (
    SELECT date_trunc('month', o.order_date)::date AS month,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o JOIN order_items oi USING (order_id)
    WHERE o.status = 'completed'
    GROUP BY 1
)
SELECT c.month, COALESCE(m.revenue, 0) AS revenue,
       SUM(COALESCE(m.revenue, 0)) OVER (ORDER BY c.month) AS cumulative_revenue,
       AVG(COALESCE(m.revenue, 0)) OVER (ORDER BY c.month ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS seven_month_average
FROM calendar c LEFT JOIN monthly m USING (month) ORDER BY c.month;

-- Top 10 customers by completed-order revenue.
SELECT c.customer_id, c.first_name, c.last_name,
       SUM(oi.quantity * oi.unit_price) AS revenue,
       COUNT(DISTINCT o.order_id) AS completed_orders,
       RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS revenue_rank,
       DENSE_RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS dense_revenue_rank
FROM customers c JOIN orders o USING (customer_id) JOIN order_items oi USING (order_id)
WHERE o.status = 'completed'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY revenue DESC LIMIT 10;

-- Daily revenue and a true seven-day moving average over calendar days.
WITH daily AS (
    SELECT o.order_date, SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o JOIN order_items oi USING (order_id)
    WHERE o.status = 'completed' GROUP BY o.order_date
), calendar AS (
    SELECT generate_series((SELECT MIN(order_date) FROM daily), (SELECT MAX(order_date) FROM daily), '1 day')::date AS order_date
)
SELECT c.order_date, COALESCE(d.revenue, 0) AS revenue,
       AVG(COALESCE(d.revenue, 0)) OVER (ORDER BY c.order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM calendar c LEFT JOIN daily d USING (order_date) ORDER BY c.order_date;

-- Cohort retention: customers are retained when they purchase in a later month.
WITH customer_cohort AS (
    SELECT customer_id, date_trunc('month', MIN(order_date))::date AS cohort_month
    FROM orders WHERE status = 'completed' GROUP BY customer_id
), activity AS (
    SELECT DISTINCT o.customer_id, cc.cohort_month, date_trunc('month', o.order_date)::date AS activity_month
    FROM orders o JOIN customer_cohort cc USING (customer_id)
    WHERE o.status = 'completed'
), cohort_sizes AS (
    SELECT cohort_month, COUNT(*) AS cohort_customers FROM customer_cohort GROUP BY cohort_month
)
SELECT a.cohort_month, ((EXTRACT(YEAR FROM a.activity_month) - EXTRACT(YEAR FROM a.cohort_month)) * 12
       + EXTRACT(MONTH FROM a.activity_month) - EXTRACT(MONTH FROM a.cohort_month))::int AS month_number,
       COUNT(*) AS retained_customers, cs.cohort_customers,
       ROUND(COUNT(*)::numeric / cs.cohort_customers, 4) AS retention_rate
FROM activity a JOIN cohort_sizes cs USING (cohort_month)
GROUP BY a.cohort_month, a.activity_month, cs.cohort_customers ORDER BY 1, 2;
