from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from .database import get_db
from . import crud
from .settings import settings
from .utils_email import send_email


router = APIRouter(prefix="/taxes", tags=["taxes"]) 


def _month_bounds(ref: date) -> tuple[datetime, datetime]:
    start = datetime(ref.year, ref.month, 1)
    if ref.month == 12:
        end = datetime(ref.year + 1, 1, 1)
    else:
        end = datetime(ref.year, ref.month + 1, 1)
    return start, end


@router.get("/monthly-summary")
def monthly_tax_summary(month: int | None = None, year: int | None = None, db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    ref = date(year or today.year, month or today.month, 1)
    start, end = _month_bounds(ref)
    revenue = crud.revenue_between(db, start, end)
    tax_rate = settings.total_tax_rate_percent
    tax_due = round(revenue * tax_rate / 100.0, 2)
    return {"period": ref.strftime("%Y-%m"), "revenue": revenue, "tax_rate_percent": tax_rate, "tax_due": tax_due}


@router.post("/send-monthly-alert")
def send_monthly_tax_alert(to_email: str | None = None, month: int | None = None, year: int | None = None, db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    ref = date(year or today.year, month or today.month, 1)
    start, end = _month_bounds(ref)
    revenue = crud.revenue_between(db, start, end)
    tax_rate = settings.total_tax_rate_percent
    tax_due = round(revenue * tax_rate / 100.0, 2)
    due_date = date(ref.year, ref.month, 20) if ref.month != 2 else date(ref.year, ref.month, 20)
    subject = f"GST/Tax Alert for {ref.strftime('%Y-%m')}"
    html = f"<p>Total Revenue: ₹ {revenue:,.2f}<br>Estimated Tax ({tax_rate}%): ₹ {tax_due:,.2f}<br>Due by: {due_date}</p>"
    send_email(subject, to_email or settings.owner_email or settings.email_from, html)
    return {"sent": True, "to": to_email or settings.owner_email or settings.email_from}

