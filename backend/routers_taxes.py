from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from .database import get_db
from . import crud, models
from .settings import settings
from .utils_email import send_email
from .routers_auth import get_current_owner


router = APIRouter(prefix="/taxes", tags=["taxes"]) 


def _month_bounds(ref: date) -> tuple[datetime, datetime]:
    start = datetime(ref.year, ref.month, 1)
    if ref.month == 12:
        end = datetime(ref.year + 1, 1, 1)
    else:
        end = datetime(ref.year, ref.month + 1, 1)
    return start, end


def _quarter_bounds(ref: date) -> tuple[datetime, datetime]:
    """Get start and end of quarter for a given date."""
    quarter = (ref.month - 1) // 3
    start_month = quarter * 3 + 1
    end_month = start_month + 3
    start = datetime(ref.year, start_month, 1)
    if end_month > 12:
        end = datetime(ref.year + 1, 1, 1)
    else:
        end = datetime(ref.year, end_month, 1)
    return start, end


def get_next_tax_deadline(today: date | None = None) -> date:
    """Get next quarterly tax deadline (29th of every 3rd month: Mar, Jun, Sep, Dec)."""
    if today is None:
        today = datetime.utcnow().date()
    
    # Quarterly deadlines: March 29, June 29, September 29, December 29
    deadlines = [
        date(today.year, 3, 29),
        date(today.year, 6, 29),
        date(today.year, 9, 29),
        date(today.year, 12, 29),
    ]
    
    # Find next deadline
    for deadline in deadlines:
        if deadline >= today:
            return deadline
    
    # If all deadlines passed this year, return first of next year
    return date(today.year + 1, 3, 29)


def get_current_quarter_deadline(today: date | None = None) -> date:
    """Get current quarter's tax deadline."""
    if today is None:
        today = datetime.utcnow().date()
    
    month = today.month
    if month <= 3:
        return date(today.year, 3, 29)
    elif month <= 6:
        return date(today.year, 6, 29)
    elif month <= 9:
        return date(today.year, 9, 29)
    else:
        return date(today.year, 12, 29)


def calculate_commercial_tax(revenue: float, owner: models.Owner | None = None) -> dict:
    """
    Calculate tax based on commercial business rules.
    Fixed 10% tax rate for small scale businesses (synchronized with reports section).
    """
    # Use fixed 10% tax rate (same as reports section)
    tax_rate = settings.total_tax_rate_percent  # 10%
    total_tax = round(revenue * (tax_rate / 100.0), 2)
    
    has_gst = owner and owner.gst_number and len(owner.gst_number.strip()) > 0
    
    return {
        "gst_registered": has_gst,
        "tax_rate": tax_rate,
        "total_tax": total_tax,
        "breakdown": {
            "Tax (10%)": total_tax,
        }
    }


@router.get("/quarterly-summary")
def quarterly_tax_summary(
    owner: models.Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Get quarterly tax summary for current quarter."""
    today = datetime.utcnow().date()
    start, end = _quarter_bounds(today)
    revenue = crud.revenue_between(db, start, end)
    
    # Calculate tax based on commercial business rules
    tax_info = calculate_commercial_tax(revenue, owner)
    deadline = get_current_quarter_deadline(today)
    
    return {
        "period": f"Q{(today.month - 1) // 3 + 1} {today.year}",
        "quarter_start": start.date().isoformat(),
        "quarter_end": (end - timedelta(days=1)).date().isoformat(),
        "revenue": revenue,
        "tax_deadline": deadline.isoformat(),
        "days_until_deadline": (deadline - today).days,
        **tax_info
    }


@router.get("/monthly-summary")
def monthly_tax_summary(
    month: int | None = None,
    year: int | None = None,
    owner: models.Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Get monthly tax summary (legacy endpoint)."""
    today = datetime.utcnow().date()
    ref = date(year or today.year, month or today.month, 1)
    start, end = _month_bounds(ref)
    revenue = crud.revenue_between(db, start, end)
    
    # Calculate tax based on commercial business rules
    tax_info = calculate_commercial_tax(revenue, owner)
    
    return {
        "period": ref.strftime("%Y-%m"),
        "revenue": revenue,
        **tax_info
    }


@router.post("/send-tax-alert")
def send_tax_alert(
    background_tasks: BackgroundTasks,
    owner: models.Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """Send tax alert email to owner's registered email."""
    today = datetime.utcnow().date()
    start, end = _quarter_bounds(today)
    revenue = crud.revenue_between(db, start, end)
    
    # Calculate tax based on commercial business rules
    tax_info = calculate_commercial_tax(revenue, owner)
    deadline = get_current_quarter_deadline(today)
    days_until = (deadline - today).days
    
    # Build tax breakdown HTML
    breakdown_html = ""
    for key, value in tax_info.get("breakdown", {}).items():
        breakdown_html += f"<li><strong>{key}:</strong> ₹ {value:,.2f}</li>"
    
    subject = f"Tax Payment Alert - Q{(today.month - 1) // 3 + 1} {today.year}"
    html = f"""
    <div style='font-family: Arial, sans-serif; padding: 20px;'>
        <h2>Tax Payment Alert</h2>
        <p><strong>Dear {owner.name},</strong></p>
        <p><strong>Quarter:</strong> Q{(today.month - 1) // 3 + 1} {today.year}</p>
        <p><strong>Total Revenue:</strong> ₹ {revenue:,.2f}</p>
        <h3>Tax Breakdown (10% Rate):</h3>
        <ul>
            {breakdown_html}
        </ul>
        <p><strong>Total Tax Due (10%):</strong> ₹ {tax_info['total_tax']:,.2f}</p>
        <p><strong>Payment Deadline:</strong> {deadline.strftime('%d %B %Y')}</p>
        <p><strong>Days Remaining:</strong> {days_until} days</p>
        <p style='color: red; font-weight: bold;'>Please ensure payment is made before the deadline to avoid penalties.</p>
        <p style='margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>
            <small>This is an automated reminder from Small Scale Business Automation system.</small>
        </p>
    </div>
    """
    
    owner_email = owner.email
    print(f"📧 Sending tax alert to owner: {owner_email}")
    background_tasks.add_task(send_email, subject, owner_email, html)
    
    return {
        "sent": True,
        "to": owner_email,
        "deadline": deadline.isoformat(),
        "days_until": days_until
    }


@router.get("/check-alerts")
def check_tax_alerts(
    background_tasks: BackgroundTasks,
    owner: models.Owner = Depends(get_current_owner),
    db: Session = Depends(get_db)
):
    """
    Check if tax alerts need to be sent (15 weeks before and 1 week before deadline).
    This should be called periodically (e.g., daily cron job).
    """
    today = datetime.utcnow().date()
    deadline = get_current_quarter_deadline(today)
    days_until = (deadline - today).days
    
    alerts_sent = []
    
    # Check if we're 15 weeks (105 days) before deadline
    if 100 <= days_until <= 110:  # 15 weeks = ~105 days, with 5 day window
        print(f"📅 15 weeks before deadline - sending early alert")
        alerts_sent.append("15_weeks")
        # Trigger alert by calling the endpoint logic
        start, end = _quarter_bounds(today)
        revenue = crud.revenue_between(db, start, end)
        tax_info = calculate_commercial_tax(revenue, owner)
        
        breakdown_html = ""
        for key, value in tax_info.get("breakdown", {}).items():
            breakdown_html += f"<li><strong>{key}:</strong> ₹ {value:,.2f}</li>"
        
        if tax_info.get("gst_registered"):
            subject = f"GST & Tax Alert (15 Weeks Remaining) - Q{(today.month - 1) // 3 + 1} {today.year}"
        else:
            subject = f"Tax Alert (15 Weeks Remaining) - Q{(today.month - 1) // 3 + 1} {today.year}"
        
        html = f"""
        <div style='font-family: Arial, sans-serif; padding: 20px;'>
            <h2>Tax Payment Reminder - 15 Weeks Before Deadline</h2>
            <p><strong>Dear {owner.name},</strong></p>
            <p><strong>Quarter:</strong> Q{(today.month - 1) // 3 + 1} {today.year}</p>
            <p><strong>Total Revenue:</strong> ₹ {revenue:,.2f}</p>
            <h3>Tax Breakdown (10% Rate):</h3>
            <ul>
                {breakdown_html}
            </ul>
            <p><strong>Total Tax Due (10%):</strong> ₹ {tax_info['total_tax']:,.2f}</p>
            <p><strong>Payment Deadline:</strong> {deadline.strftime('%d %B %Y')}</p>
            <p><strong>Days Remaining:</strong> {days_until} days (15 weeks)</p>
            <p style='color: orange; font-weight: bold;'>Early reminder: Please plan your tax payment accordingly.</p>
            <p style='margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>
                <small>This is an automated reminder from Small Scale Business Automation system.</small>
            </p>
        </div>
        """
        background_tasks.add_task(send_email, subject, owner.email, html)
    
    # Check if we're 1 week (7 days) before deadline - AUTOMATED EMAIL
    elif 5 <= days_until <= 9:  # 1 week = 7 days, with 2 day window
        print(f"📅 1 week before deadline - sending AUTOMATED final alert to {owner.email}")
        alerts_sent.append("1_week")
        # Trigger alert by calling the endpoint logic
        start, end = _quarter_bounds(today)
        revenue = crud.revenue_between(db, start, end)
        tax_info = calculate_commercial_tax(revenue, owner)
        
        breakdown_html = ""
        for key, value in tax_info.get("breakdown", {}).items():
            breakdown_html += f"<li><strong>{key}:</strong> ₹ {value:,.2f}</li>"
        
        subject = f"⚠️ URGENT: Tax Payment Due in 1 Week - Q{(today.month - 1) // 3 + 1} {today.year}"
        
        html = f"""
        <div style='font-family: Arial, sans-serif; padding: 20px;'>
            <h2 style='color: red;'>⚠️ URGENT: Tax Payment Due in 1 Week</h2>
            <p><strong>Dear {owner.name},</strong></p>
            <p><strong>Quarter:</strong> Q{(today.month - 1) // 3 + 1} {today.year}</p>
            <p><strong>Total Revenue:</strong> ₹ {revenue:,.2f}</p>
            <h3>Tax Breakdown (10% Rate):</h3>
            <ul>
                {breakdown_html}
            </ul>
            <p><strong>Total Tax Due (10%):</strong> ₹ {tax_info['total_tax']:,.2f}</p>
            <p><strong>Payment Deadline:</strong> {deadline.strftime('%d %B %Y')}</p>
            <p><strong>Days Remaining:</strong> {days_until} days (1 week)</p>
            <p style='color: red; font-weight: bold; font-size: 16px;'>⚠️ Please make payment immediately to avoid penalties and late fees.</p>
            <p style='margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>
                <small>This is an automated reminder from Small Scale Business Automation system.</small>
            </p>
        </div>
        """
        # Send email directly (not as background task for reliability)
        send_email(subject, owner.email, html)
        print(f"✅ Automated tax alert sent to {owner.email}")
    
    return {
        "deadline": deadline.isoformat(),
        "days_until": days_until,
        "alerts_sent": alerts_sent,
        "next_deadline": get_next_tax_deadline(today).isoformat()
    }


@router.post("/auto-check-alerts")
def auto_check_all_owners_alerts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Automated endpoint to check and send tax alerts for ALL owners.
    This should be called daily via cron job or scheduled task.
    No authentication required (for automated systems).
    """
    today = datetime.utcnow().date()
    owners = db.execute(
        select(models.Owner).where(models.Owner.is_active == True)
    ).scalars().all()
    
    alerts_sent_count = 0
    
    for owner in owners:
        try:
            deadline = get_current_quarter_deadline(today)
            days_until = (deadline - today).days
            
            # Send alert if 1 week (7 days) before deadline
            if 5 <= days_until <= 9:
                start, end = _quarter_bounds(today)
                revenue = crud.revenue_between(db, start, end)
                tax_info = calculate_commercial_tax(revenue, owner)
                
                breakdown_html = ""
                for key, value in tax_info.get("breakdown", {}).items():
                    breakdown_html += f"<li><strong>{key}:</strong> ₹ {value:,.2f}</li>"
                
                subject = f"⚠️ URGENT: Tax Payment Due in 1 Week - Q{(today.month - 1) // 3 + 1} {today.year}"
                
                html = f"""
                <div style='font-family: Arial, sans-serif; padding: 20px;'>
                    <h2 style='color: red;'>⚠️ URGENT: Tax Payment Due in 1 Week</h2>
                    <p><strong>Dear {owner.name},</strong></p>
                    <p><strong>Quarter:</strong> Q{(today.month - 1) // 3 + 1} {today.year}</p>
                    <p><strong>Total Revenue:</strong> ₹ {revenue:,.2f}</p>
                    <h3>Tax Breakdown (10% Rate):</h3>
                    <ul>
                        {breakdown_html}
                    </ul>
                    <p><strong>Total Tax Due (10%):</strong> ₹ {tax_info['total_tax']:,.2f}</p>
                    <p><strong>Payment Deadline:</strong> {deadline.strftime('%d %B %Y')}</p>
                    <p><strong>Days Remaining:</strong> {days_until} days (1 week)</p>
                    <p style='color: red; font-weight: bold; font-size: 16px;'>⚠️ Please make payment immediately to avoid penalties and late fees.</p>
                    <p style='margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>
                        <small>This is an automated reminder from Small Scale Business Automation system.</small>
                    </p>
                </div>
                """
                
                background_tasks.add_task(send_email, subject, owner.email, html)
                alerts_sent_count += 1
                print(f"✅ Automated tax alert queued for {owner.email}")
                
        except Exception as e:
            print(f"❌ Error processing owner {owner.email}: {str(e)}")
            continue
    
    return {
        "checked_owners": len(owners),
        "alerts_sent": alerts_sent_count,
        "date": today.isoformat()
    }

