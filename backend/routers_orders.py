from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, schemas, models
from .utils_email import send_email
from .utils_gemini import generate_email_content
from .settings import settings


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)


@router.post("/", response_model=schemas.OrderOut)
def place_order(
    payload: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    try:
        order = crud.place_order(db, payload)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    order = crud.get_order_with_details(db, order.id) or order

    # Email to owner
    owner_subject = f"New Order #{order.id} placed"
    owner_body = generate_email_content(
        (
            "Summarize an order confirmation for the store owner. "
            f"Order ID {order.id} total {order.total_amount}."
        )
    )
    background_tasks.add_task(
        send_email,
        owner_subject,
        settings.owner_email or settings.email_from,
        f"<p>{owner_body}</p>",
    )

    # Email to customer
    customer_email = order.customer.email
    cust_subj = f"Order #{order.id} Confirmation"
    cust_body = generate_email_content(
        (
            "Write a friendly order confirmation email to customer "
            f"{order.customer.name}. "
            f"Order ID {order.id}, total {order.total_amount}."
        )
    )
    background_tasks.add_task(
        send_email,
        cust_subj,
        customer_email,
        f"<p>{cust_body}</p>",
    )

    # Out-of-stock alerts to owner
    for oi in order.items:
        item = db.get(models.Item, oi.item_id)
        if item and item.stock_quantity <= 0:
            alert_subj = f"Out of Stock: {item.name}"
            alert_body = generate_email_content(
                (
                    "Inform the store owner that item '"
                    f"{item.name}' is out of stock on order {order.id}."
                )
            )
            background_tasks.add_task(
                send_email,
                alert_subj,
                settings.owner_email or settings.email_from,
                f"<p>{alert_body}</p>",
            )

    return order


@router.patch("/{order_id}/status", response_model=schemas.OrderOut)
def update_status(
    order_id: int,
    payload: schemas.OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    order = crud.update_order_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.commit()
    order = crud.get_order_with_details(db, order.id) or order

    # notify customer on status change
    cust_subj = f"Order #{order.id} {order.status.value.capitalize()}"
    cust_body = generate_email_content(
        (
            "Tell the customer that their order "
            f"{order.id} is now {order.status.value}."
        )
    )
    background_tasks.add_task(
        send_email,
        cust_subj,
        order.customer.email,
        f"<p>{cust_body}</p>",
    )

    return order


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_with_details(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
