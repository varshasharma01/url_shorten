"""
Database models (schema) for Webvory Backend Assignment.

Tables:
    - customers
    - orders
    - refunds

Includes indexes on columns used heavily by analytics queries.
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index
from database.connection import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name        = Column(String(100))
    email       = Column(String(100), unique=True)
    phone       = Column(String(20))
    city        = Column(String(50))
    country     = Column(String(5))
    created_at  = Column(Date)


class Order(Base):
    __tablename__ = "orders"

    order_id         = Column(Integer, primary_key=True)
    customer_id      = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    order_date       = Column(Date, nullable=False)
    amount           = Column(Numeric(10, 2), nullable=False)
    status           = Column(String(20), nullable=False)
    product_category = Column(String(50))

    __table_args__ = (
        Index("idx_orders_customer_id", "customer_id"),
        Index("idx_orders_order_date", "order_date"),
        Index("idx_orders_status", "status"),
        # Composite index: most analytics queries filter status + date together
        Index("idx_orders_status_date", "status", "order_date"),
    )


class Refund(Base):
    __tablename__ = "refunds"

    refund_id     = Column(Integer, primary_key=True)
    order_id      = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    customer_id   = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    refund_date   = Column(Date, nullable=False)
    refund_amount = Column(Numeric(10, 2), nullable=False)
    reason        = Column(String(100))

    __table_args__ = (
        Index("idx_refunds_order_id", "order_id"),
        Index("idx_refunds_customer_id", "customer_id"),
    )