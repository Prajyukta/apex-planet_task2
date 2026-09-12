SET search_path TO ecommerce, public;

CREATE OR REPLACE VIEW monthly_sales AS
SELECT date_trunc('month', o.order_date)::date AS month,
       SUM(oi.quantity * oi.unit_price) AS revenue,
       COUNT(DISTINCT o.order_id) AS orders,
       SUM(oi.quantity) AS units
FROM orders o JOIN order_items oi USING (order_id)
WHERE o.status = 'completed'
GROUP BY 1;

CREATE OR REPLACE VIEW customer_revenue AS
SELECT c.customer_id, c.first_name, c.last_name, c.email,
       COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue,
       COUNT(DISTINCT o.order_id) AS completed_orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id AND o.status = 'completed'
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email;

CREATE OR REPLACE VIEW product_performance AS
SELECT p.product_id, p.product_name, p.category,
    COALESCE(SUM(oi.quantity) FILTER (WHERE o.order_id IS NOT NULL), 0) AS units_sold,
    COALESCE(SUM(oi.quantity * oi.unit_price) FILTER (WHERE o.order_id IS NOT NULL), 0) AS revenue
FROM products p LEFT JOIN order_items oi USING (product_id)
LEFT JOIN orders o ON o.order_id = oi.order_id AND o.status = 'completed'
GROUP BY p.product_id, p.product_name, p.category;
