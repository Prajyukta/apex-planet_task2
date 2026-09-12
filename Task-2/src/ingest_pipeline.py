"""Normalize Online Retail II and load it into PostgreSQL."""

from pathlib import Path

import pandas as pd

from .config import get_settings
from .db_utils import DatabaseManager

RAW_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "online_retail_II.csv"


def normalize_retail_csv(raw_file: Path = RAW_FILE) -> dict[str, pd.DataFrame]:
    """Convert the denormalized export into the four relational tables."""
    frame = pd.read_csv(raw_file, low_memory=False)
    frame.columns = frame.columns.str.strip()
    frame["Invoice"] = frame["Invoice"].astype(str).str.strip()
    frame["StockCode"] = frame["StockCode"].astype(str).str.strip()
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    frame["Customer ID"] = pd.to_numeric(frame["Customer ID"], errors="coerce")
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["Price"] = pd.to_numeric(frame["Price"], errors="coerce")
    frame = frame.dropna(subset=["Invoice", "StockCode", "InvoiceDate", "Quantity", "Price"])
    frame = frame[frame["Quantity"] != 0].copy()
    frame["customer_id"] = frame["Customer ID"].round().astype("Int64")
    frame = frame.dropna(subset=["customer_id"])
    frame["customer_id"] = frame["customer_id"].astype(str)
    frame["status"] = frame["Invoice"].str.startswith("C").map({True: "cancelled", False: "completed"})
    frame["Quantity"] = frame["Quantity"].abs()

    customers = (frame.groupby("customer_id", as_index=False)
                 .agg(signup_date=("InvoiceDate", "min"), country=("Country", "first")))
    customers[["first_name", "last_name"]] = ""
    customers["email"] = customers["customer_id"].map(lambda value: f"customer-{value}@retail.local")
    customers = customers[["customer_id", "first_name", "last_name", "email", "signup_date", "country"]]
    customers["signup_date"] = customers["signup_date"].dt.date

    products = (frame.groupby("StockCode", as_index=False)
                .agg(product_name=("Description", "first"), category=("Country", "first"), unit_price=("Price", "first"))
                .rename(columns={"StockCode": "product_id"}))
    orders = (frame.groupby("Invoice", as_index=False)
              .agg(customer_id=("customer_id", "first"), order_date=("InvoiceDate", "min"), status=("status", "first"))
              .rename(columns={"Invoice": "order_id"}))
    orders["order_date"] = orders["order_date"].dt.date
    items = (frame.rename(columns={"Invoice": "order_id", "StockCode": "product_id", "Quantity": "quantity", "Price": "unit_price"})
             .groupby(["order_id", "product_id"], as_index=False)
             .agg(quantity=("quantity", "sum"), unit_price=("unit_price", "first")))
    items["order_item_id"] = items.index + 1
    items = items[["order_item_id", "order_id", "product_id", "quantity", "unit_price"]]
    return {"customers": customers, "products": products, "orders": orders, "order_items": items}


def load_csv(db: DatabaseManager, raw_file: Path = RAW_FILE) -> None:
    """Replace normalized tables with records derived from the raw export."""
    tables = normalize_retail_csv(raw_file)
    with db.engine.begin() as connection:
        connection.exec_driver_sql("TRUNCATE TABLE ecommerce.order_items, ecommerce.orders, ecommerce.customers, ecommerce.products CASCADE")
        for table, frame in tables.items():
            frame.to_sql(table, connection, schema="ecommerce", if_exists="append", index=False, method="multi")
            print(f"Loaded {len(frame):,} rows into ecommerce.{table}")


if __name__ == "__main__":
    manager = DatabaseManager(get_settings())
    try:
        load_csv(manager)
    finally:
        manager.close()
