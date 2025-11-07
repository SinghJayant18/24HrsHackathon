from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    Enum as SAEnum,
    Boolean,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base


class OrderStatus(str, Enum):
    placed = "placed"
    processing = "processing"
    dispatched = "dispatched"
    delivered = "delivered"
    cancelled = "cancelled"


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0.0)
    image_url: Mapped[str | None] = mapped_column(String(500), default=None)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="item"
    )


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), index=True)
    address: Mapped[str | None] = mapped_column(Text, default=None)
    phone: Mapped[str | None] = mapped_column(String(50), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="customer"
    )


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.placed
    )
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    tracking_id: Mapped[str | None] = mapped_column(String(200), default=None)
    tracking_url: Mapped[str | None] = mapped_column(String(500), default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    customer: Mapped[Customer] = relationship(
        "Customer", back_populates="orders"
    )
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price_at_purchase: Mapped[float] = mapped_column(Float, default=0.0)

    order: Mapped[Order] = relationship("Order", back_populates="items")
    item: Mapped[Item] = relationship("Item", back_populates="order_items")
