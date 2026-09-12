SET search_path TO ecommerce, public;

-- Capture a baseline before adding indexes in a populated environment.
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o JOIN order_items oi USING (order_id)
WHERE o.status = 'completed' AND o.order_date >= DATE '2024-01-01'
GROUP BY o.customer_id ORDER BY revenue DESC;

CREATE INDEX IF NOT EXISTS idx_orders_status_date ON orders (status, order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders (customer_id, order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);

-- Compare this plan with the baseline and retain only indexes justified by workload.
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o JOIN order_items oi USING (order_id)
WHERE o.status = 'completed' AND o.order_date >= DATE '2024-01-01'
GROUP BY o.customer_id ORDER BY revenue DESC;
