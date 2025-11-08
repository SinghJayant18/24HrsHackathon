from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from .database import get_db
from . import crud, schemas
from .utils_pdf import generate_revenue_report_pdf
from .settings import settings


router = APIRouter(prefix="/reports", tags=["reports"])


def _period_bounds(period: str, ref: date | None = None) -> tuple[datetime, datetime, str]:
    today = datetime.utcnow().date()
    if period == "day":
        refd = ref or today
        start = datetime(refd.year, refd.month, refd.day)
        end = start + timedelta(days=1)
        label = start.strftime("%Y-%m-%d")
    elif period == "month":
        refd = ref or date(today.year, today.month, 1)
        start = datetime(refd.year, refd.month, 1)
        if refd.month == 12:
            end = datetime(refd.year + 1, 1, 1)
        else:
            end = datetime(refd.year, refd.month + 1, 1)
        label = start.strftime("%Y-%m")
    elif period == "year":
        refd = ref or date(today.year, 1, 1)
        start = datetime(refd.year, 1, 1)
        end = datetime(refd.year + 1, 1, 1)
        label = start.strftime("%Y")
    else:
        raise ValueError("Invalid period")
    return start, end, label


@router.get("/revenue/pdf")
def revenue_pdf(period: str, date_ref: date | None = None, db: Session = Depends(get_db)):
    try:
        start, end, label = _period_bounds(period, date_ref)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid period; use day|month|year")
    revenue = crud.revenue_between(db, start, end)
    tax_rate = settings.total_tax_rate_percent
    tax_due = round(revenue * tax_rate / 100.0, 2)
    pdf = generate_revenue_report_pdf(f"{period.upper()} {label}", revenue, details=[("Estimated Tax", tax_due)])
    headers = {"Content-Disposition": f"attachment; filename=revenue_{period}_{label}.pdf"}
    return Response(content=pdf, media_type="application/pdf", headers=headers)


@router.get("/revenue/tax", response_model=schemas.TaxSummary)
def revenue_tax(period: str, date_ref: date | None = None, db: Session = Depends(get_db)):
    start, end, label = _period_bounds(period, date_ref)
    revenue = crud.revenue_between(db, start, end)
    tax_rate = settings.total_tax_rate_percent
    tax_due = round(revenue * tax_rate / 100.0, 2)
    return schemas.TaxSummary(
        total_revenue=revenue, tax_rate_percent=tax_rate, total_tax_due=tax_due, period=label
    )

