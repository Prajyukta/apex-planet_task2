-- Run with psql from the project root after the schema exists.
-- The Python ingest_pipeline.py is preferred for repeatable local loads.
SET search_path TO ecommerce, public;

\copy customers (customer_id, first_name, last_name, email, signup_date, country) FROM 'data/processed/customers.csv' WITH (FORMAT csv, HEADER true)
\copy products (product_id, product_name, category, unit_price) FROM 'data/processed/products.csv' WITH (FORMAT csv, HEADER true)
\copy orders (order_id, customer_id, order_date, status) FROM 'data/processed/orders.csv' WITH (FORMAT csv, HEADER true)
\copy order_items (order_item_id, order_id, product_id, quantity, unit_price) FROM 'data/processed/order_items.csv' WITH (FORMAT csv, HEADER true)
