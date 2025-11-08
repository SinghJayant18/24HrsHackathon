from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from datetime import datetime
from . import models, schemas


def create_or_get_customer(
    db: Session, data: schemas.CustomerCreate
) -> models.Customer:
    existing = db.execute(
        select(models.Customer).where(models.Customer.email == data.email)
    ).scalar_one_or_none()
    if existing:
        # Update basic fields if changed
        existing.name = data.name
        existing.address = data.address
        existing.phone = data.phone
        db.add(existing)
        db.flush()
        return existing
    customer = models.Customer(
        name=data.name,
        email=data.email,
        address=data.address,
        phone=data.phone,
    )
    db.add(customer)
    db.flush()
    return customer


def create_item(db: Session, data: schemas.ItemCreate) -> models.Item:
    item = models.Item(**data.model_dump())
    db.add(item)
    db.flush()
    return item


def update_item(
    db: Session, item_id: int, data: schemas.ItemUpdate
) -> models.Item | None:
    item = db.get(models.Item, item_id)
    if not item:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.add(item)
    db.flush()
    return item


def list_items(db: Session) -> list[models.Item]:
    return list(
        db.execute(select(models.Item).order_by(models.Item.name)).scalars()
    )


def get_item(db: Session, item_id: int) -> models.Item | None:
    return db.get(models.Item, item_id)


def place_order(db: Session, data: schemas.OrderCreate) -> models.Order:
    customer = create_or_get_customer(db, data.customer)
    order = models.Order(
        customer_id=customer.id, status=models.OrderStatus.placed
    )
    db.add(order)
    db.flush()
    total = 0.0
    for oi in data.items:
        item = db.get(models.Item, oi.item_id)
        if not item or not item.is_active:
            raise ValueError("Invalid item in order")
        if item.stock_quantity < oi.quantity:
            raise ValueError("Insufficient stock for item: " + item.name)
        price = item.price * (1 - (item.discount_percent or 0.0) / 100.0)
        total += price * oi.quantity
        # reduce stock
        item.stock_quantity -= oi.quantity
        db.add(item)
        db.flush()
        db.add(
            models.OrderItem(
                order_id=order.id,
                item_id=item.id,
                quantity=oi.quantity,
                price_at_purchase=price,
            )
        )
    order.total_amount = round(total, 2)
    db.add(order)
    db.flush()
    db.refresh(order)
    return order


def update_order_status(
    db: Session, order_id: int, status: models.OrderStatus
) -> models.Order | None:
    order = db.get(models.Order, order_id)
    if not order:
        return None
    order.status = status
    db.add(order)
    db.flush()
    db.refresh(order)
    return order


def revenue_between(
    db: Session, start_dt: datetime, end_dt: datetime
) -> float:
    q = select(func.coalesce(func.sum(models.Order.total_amount), 0.0)).where(
        models.Order.created_at >= start_dt,
        models.Order.created_at < end_dt,
        models.Order.status != models.OrderStatus.cancelled,
    )
    return float(db.execute(q).scalar_one() or 0.0)


def orders_between(
    db: Session, start_dt: datetime, end_dt: datetime
) -> list[models.Order]:
    q = select(models.Order).where(
        models.Order.created_at >= start_dt, models.Order.created_at < end_dt
    )
    return list(db.execute(q).scalars())


def list_orders(db: Session) -> list[models.Order]:
    q = (
        select(models.Order)
        .options(
            selectinload(models.Order.customer),
            selectinload(models.Order.items).selectinload(
                models.OrderItem.item
            ),
        )
        .order_by(models.Order.created_at.desc())
    )
    return list(db.execute(q).scalars())


def get_order_with_details(db: Session, order_id: int) -> models.Order | None:
    q = (
        select(models.Order)
        .options(
            selectinload(models.Order.customer),
            selectinload(models.Order.items).selectinload(
                models.OrderItem.item
            ),
        )
        .where(models.Order.id == order_id)
    )
    return db.execute(q).scalar_one_or_none()
