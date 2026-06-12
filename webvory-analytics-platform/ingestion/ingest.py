"""
Ingestion Service for Webvory Backend Assignment.

Pulls paginated data from the Mock API (/customers, /orders, /refunds)
and bulk-inserts into PostgreSQL using batched commits.

Run AFTER:
    1. PostgreSQL is running and 'webvory_db' database exists
    2. Mock API is running on http://localhost:8001

Run:
    python -m ingestion.ingest
"""

import time
import requests
from database.connection import engine, SessionLocal, Base
from database.models import Customer, Order, Refund

MOCK_API_BASE = "http://localhost:8001"
PAGE_SIZE = 2000   # records per API call


# ──────────────────────────────────────────────
# Create tables (if not already created)
# ──────────────────────────────────────────────

def create_tables():
    print("Creating tables (if not exist)...")
    Base.metadata.create_all(bind=engine)
    print("Tables ready.\n")


# ──────────────────────────────────────────────
# Generic ingestion function
# ──────────────────────────────────────────────

def ingest_endpoint(endpoint: str, model, row_mapper, label: str):
    """
    endpoint   : '/customers', '/orders', '/refunds'
    model      : SQLAlchemy model class (Customer, Order, Refund)
    row_mapper : function converting API row (dict, all strings) -> dict matching model columns
    label      : friendly name for logging
    """
    print(f"Ingesting {label}...")
    start_time = time.time()

    session = SessionLocal()
    page = 1
    total_inserted = 0

    try:
        while True:
            response = requests.get(
                f"{MOCK_API_BASE}{endpoint}",
                params={"page": page, "size": PAGE_SIZE},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()

            rows = payload["data"]
            if not rows:
                break  # no more data

            # Convert API rows (strings) -> typed dicts matching DB columns
            mapped_rows = [row_mapper(r) for r in rows]

            # Bulk insert this page
            session.bulk_insert_mappings(model, mapped_rows)
            session.commit()

            total_inserted += len(mapped_rows)

            if page % 10 == 0 or page == 1:
                print(f"  {label}: page {page}/{payload['total_pages']} "
                      f"({total_inserted:,}/{payload['total']:,} rows)")

            if page >= payload["total_pages"]:
                break

            page += 1

    finally:
        session.close()

    elapsed = time.time() - start_time
    print(f"  Done. {total_inserted:,} {label} inserted in {elapsed:.1f}s\n")


# ──────────────────────────────────────────────
# Row mappers — convert raw API strings to typed values
# ──────────────────────────────────────────────

def map_customer(r: dict) -> dict:
    return {
        "customer_id": int(r["customer_id"]),
        "name": r["name"],
        "email": r["email"],
        "phone": r["phone"],
        "city": r["city"],
        "country": r["country"],
        "created_at": r["created_at"],
    }


def map_order(r: dict) -> dict:
    return {
        "order_id": int(r["order_id"]),
        "customer_id": int(r["customer_id"]),
        "order_date": r["order_date"],
        "amount": float(r["amount"]),
        "status": r["status"],
        "product_category": r["product_category"],
    }


def map_refund(r: dict) -> dict:
    return {
        "refund_id": int(r["refund_id"]),
        "order_id": int(r["order_id"]),
        "customer_id": int(r["customer_id"]),
        "refund_date": r["refund_date"],
        "refund_amount": float(r["refund_amount"]),
        "reason": r["reason"],
    }


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    overall_start = time.time()
    print("=" * 50)
    print("  Webvory Ingestion Service")
    print("=" * 50 + "\n")

    create_tables()

    # Order matters: customers first (orders/refunds reference customer_id)
    ingest_endpoint("/customers", Customer, map_customer, "customers")
    ingest_endpoint("/orders", Order, map_order, "orders")
    ingest_endpoint("/refunds", Refund, map_refund, "refunds")

    elapsed = time.time() - overall_start
    print("=" * 50)
    print(f"  All ingestion complete in {elapsed:.1f}s")
    print("=" * 50)