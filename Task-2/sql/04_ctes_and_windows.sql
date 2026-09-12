SET search_path TO ecommerce, public;

WITH completed_orders AS (
    SELECT order_id, customer_id, order_date
    FROM orders WHERE status = 'completed'
), order_revenue AS (
    SELECT o.order_id, o.customer_id, o.order_date,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM completed_orders o JOIN order_items oi USING (order_id)
    GROUP BY o.order_id, o.customer_id, o.order_date
)
SELECT *, SUM(revenue) OVER (PARTITION BY customer_id ORDER BY order_date, order_id
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS customer_running_total,
          ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS purchase_number,
          LAG(revenue) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS previous_order_revenue,
          LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS next_order_date
FROM order_revenue ORDER BY order_date, order_id;

-- Subquery: customers whose revenue is above the average customer revenue.
SELECT customer_id, revenue
FROM (SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue
      FROM orders o JOIN order_items oi USING (order_id)
      WHERE o.status = 'completed'
      GROUP BY o.customer_id) customer_totals
WHERE revenue > (SELECT AVG(revenue) FROM (
    SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o JOIN order_items oi USING (order_id)
    WHERE o.status = 'completed' GROUP BY o.customer_id
) averages);
