from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from .database import get_db
from . import crud, schemas, models
from .utils_email import send_email, send_email_with_pdf
from .utils_gemini import generate_order_status_email
from .utils_geocoding import parse_address_for_coords, calculate_expected_delivery
from .utils_pdf import generate_ebill_pdf
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

    # Auto-assign tracking ID (same as order ID)
    order.tracking_id = str(order.id)
    
    # Auto-parse lat/lng from customer address
    lat, lng = parse_address_for_coords(order.customer.address)
    if lat and lng:
        order.tracking_url = f"https://www.google.com/maps?q={lat},{lng}"
    
    # Calculate expected delivery date (max 5 days)
    delivery_date, delivery_str = calculate_expected_delivery(
        order.created_at, order.customer.address
    )
    order.expected_delivery_date = delivery_date
    
    db.add(order)
    db.commit()
    db.refresh(order)

    # Prepare items summary for email
    items_summary = ", ".join(
        [
            f"{oi.item.name if oi.item else f'Item {oi.item_id}'} (×{oi.quantity})"
            for oi in order.items
        ]
    )

    # Generate e-bill PDF
    order_dict = {
        "id": order.id,
        "status": order.status.value if hasattr(order.status, "value") else str(order.status),
        "total_amount": order.total_amount,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "customer": {
            "name": order.customer.name,
            "email": order.customer.email,
            "address": order.customer.address,
            "phone": order.customer.phone,
        },
        "items": [
            {
                "id": oi.id,
                "item_id": oi.item_id,
                "quantity": oi.quantity,
                "price_at_purchase": oi.price_at_purchase,
                "item": {
                    "name": oi.item.name if oi.item else f"Item {oi.item_id}",
                    "discount_percent": oi.item.discount_percent if oi.item else 0.0,
                },
            }
            for oi in order.items
        ],
    }
    pdf_data = generate_ebill_pdf(order_dict)

    # Email to customer with e-bill PDF for PLACED status
    customer_email = order.customer.email
    cust_subj = f"Order #{order.id} Confirmation - E-Bill Attached"
    cust_body_html = generate_order_status_email(
        customer_name=order.customer.name,
        order_id=order.id,
        status="placed",
        status_change_time=order.created_at,
        expected_delivery=delivery_str,
        total_amount=order.total_amount,
        items_summary=items_summary,
    )
    print(f"📧 Sending PLACED status email to customer: {customer_email}")
    background_tasks.add_task(
        send_email_with_pdf,
        cust_subj,
        customer_email,
        f"<div style='font-family: Arial, sans-serif; padding: 20px;'>{cust_body_html.replace(chr(10), '<br>')}</div>",
        pdf_data,
        f"Order_{order.id}_E-Bill.pdf",
    )

    # Email to owner
    owner_subject = f"New Order #{order.id} placed"
    owner_body = f"""
    <div style='font-family: Arial, sans-serif; padding: 20px;'>
        <h2>New Order Received</h2>
        <p><strong>Order ID:</strong> #{order.id}</p>
        <p><strong>Customer:</strong> {order.customer.name} ({order.customer.email})</p>
        <p><strong>Total Amount:</strong> ₹{order.total_amount:.2f}</p>
        <p><strong>Items:</strong> {items_summary}</p>
        <p><strong>Expected Delivery:</strong> {delivery_str}</p>
        <p><strong>Address:</strong> {order.customer.address or 'N/A'}</p>
    </div>
    """
    background_tasks.add_task(
        send_email,
        owner_subject,
        settings.owner_email or settings.email_from,
        owner_body,
    )

    # Out-of-stock alerts to owner
    for oi in order.items:
        item = db.get(models.Item, oi.item_id)
        if item and item.stock_quantity <= 0:
            alert_subj = f"Out of Stock: {item.name}"
            alert_body = f"""
            <div style='font-family: Arial, sans-serif; padding: 20px;'>
                <h3>Out of Stock Alert</h3>
                <p>Item <strong>{item.name}</strong> is now out of stock after order #{order.id}.</p>
                <p>Date: {datetime.utcnow().strftime('%d %B %Y at %I:%M %p')}</p>
            </div>
            """
            background_tasks.add_task(
                send_email,
                alert_subj,
                settings.owner_email or settings.email_from,
                alert_body,
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

    status_change_time = datetime.utcnow()
    status_value = order.status.value if hasattr(order.status, "value") else str(order.status)

    # Prepare items summary
    items_summary = ", ".join(
        [
            f"{oi.item.name if oi.item else f'Item {oi.item_id}'} (×{oi.quantity})"
            for oi in order.items
        ]
    )

    # Get expected delivery date string
    delivery_str = None
    if order.expected_delivery_date:
        delivery_str = order.expected_delivery_date.strftime("%d %b %Y, %I:%M %p")

    # Generate e-bill PDF
    order_dict = {
        "id": order.id,
        "status": status_value,
        "total_amount": order.total_amount,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "customer": {
            "name": order.customer.name,
            "email": order.customer.email,
            "address": order.customer.address,
            "phone": order.customer.phone,
        },
        "items": [
            {
                "id": oi.id,
                "item_id": oi.item_id,
                "quantity": oi.quantity,
                "price_at_purchase": oi.price_at_purchase,
                "item": {
                    "name": oi.item.name if oi.item else f"Item {oi.item_id}",
                    "discount_percent": oi.item.discount_percent if oi.item else 0.0,
                },
            }
            for oi in order.items
        ],
    }
    pdf_data = generate_ebill_pdf(order_dict)

    # Generate professional email content using Gemini
    cust_body_html = generate_order_status_email(
        customer_name=order.customer.name,
        order_id=order.id,
        status=status_value,
        status_change_time=status_change_time,
        expected_delivery=delivery_str,
        total_amount=order.total_amount,
        items_summary=items_summary,
    )

    # Email to customer for ALL status changes (PLACED, PROCESSING, DISPATCHED, DELIVERED, CANCELLED)
    status_subjects = {
        "placed": f"Order #{order.id} Confirmation - E-Bill Attached",
        "processing": f"Order #{order.id} is Being Processed - E-Bill Attached",
        "dispatched": f"Order #{order.id} Has Been Dispatched - E-Bill Attached",
        "delivered": f"Order #{order.id} Delivered Successfully - E-Bill Attached",
        "cancelled": f"Order #{order.id} Cancellation Notice - E-Bill Attached",
    }
    
    cust_subj = status_subjects.get(status_value.lower(), f"Order #{order.id} {status_value.capitalize()} - E-Bill Attached")
    
    # Send email to customer for every status change
    print(f"📧 Sending {status_value.upper()} status email to customer: {order.customer.email}")
    background_tasks.add_task(
        send_email_with_pdf,
        cust_subj,
        order.customer.email,
        f"<div style='font-family: Arial, sans-serif; padding: 20px;'>{cust_body_html.replace(chr(10), '<br>')}</div>",
        pdf_data,
        f"Order_{order.id}_E-Bill.pdf",
    )

    # If order is cancelled, also notify owner
    if status_value.lower() == "cancelled":
        owner_subj = f"Order #{order.id} Cancelled"
        owner_body = f"""
        <div style='font-family: Arial, sans-serif; padding: 20px;'>
            <h2>Order Cancelled</h2>
            <p><strong>Order ID:</strong> #{order.id}</p>
            <p><strong>Customer:</strong> {order.customer.name} ({order.customer.email})</p>
            <p><strong>Total Amount:</strong> ₹{order.total_amount:.2f}</p>
            <p><strong>Cancelled On:</strong> {status_change_time.strftime('%d %B %Y at %I:%M %p')}</p>
        </div>
        """
        background_tasks.add_task(
            send_email,
            owner_subj,
            settings.owner_email or settings.email_from,
            owner_body,
        )

    return order


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_with_details(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
