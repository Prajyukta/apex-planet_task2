SET search_path TO ecommerce, public;

-- Filtering, sorting, and pagination.
SELECT order_id, customer_id, order_date, status
FROM orders
WHERE status = 'completed' AND order_date >= DATE '2024-01-01'
ORDER BY order_date DESC, order_id DESC
LIMIT 10 OFFSET 0;

-- INNER JOIN: only customers with orders.
SELECT c.customer_id, c.email, o.order_id, o.order_date
FROM customers c INNER JOIN orders o ON o.customer_id = c.customer_id;

-- LEFT, RIGHT, and FULL OUTER JOIN examples.
SELECT c.customer_id, c.email, o.order_id
FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id;
SELECT p.product_id, p.product_name, oi.order_id
FROM order_items oi RIGHT JOIN products p ON p.product_id = oi.product_id;
SELECT c.customer_id, o.order_id
FROM customers c FULL OUTER JOIN orders o ON o.customer_id = c.customer_id;

-- Aggregation uses captured item prices and excludes cancelled orders.
SELECT p.category, COUNT(DISTINCT o.order_id) AS orders, SUM(oi.quantity) AS units,
       SUM(oi.quantity * oi.unit_price) AS revenue, AVG(oi.unit_price) AS avg_item_price,
       MIN(oi.unit_price) AS min_item_price, MAX(oi.unit_price) AS max_item_price
FROM products p
JOIN order_items oi ON oi.product_id = p.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY p.category
HAVING SUM(oi.quantity * oi.unit_price) > 100
ORDER BY revenue DESC;
