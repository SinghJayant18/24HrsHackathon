from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models


router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/{order_id}/assign")
def assign_tracking(order_id: int, tracking_id: str, lat: float | None = None, lng: float | None = None, db: Session = Depends(get_db)):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.tracking_id = tracking_id
    # Generate a Google Maps link for dispatch location (if provided)
    if lat is not None and lng is not None:
        order.tracking_url = f"https://www.google.com/maps?q={lat},{lng}"
    db.add(order)
    db.commit()
    return {"order_id": order_id, "tracking_id": order.tracking_id, "tracking_url": order.tracking_url}


@router.get("/{order_id}")
def get_tracking(order_id: int, db: Session = Depends(get_db)):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "tracking_id": order.tracking_id, "tracking_url": order.tracking_url, "status": order.status}

