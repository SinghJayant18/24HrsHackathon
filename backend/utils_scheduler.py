"""
Background scheduler for automated tax alerts.
This should be called periodically (e.g., daily via cron or scheduled task).
"""
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from .routers_taxes import check_tax_alerts, get_current_quarter_deadline
from . import models
from sqlalchemy import select


async def check_and_send_tax_alerts():
    """
    Check all active owners and send tax alerts if needed.
    This function should be called daily (e.g., via cron job or scheduled task).
    """
    db: Session = SessionLocal()
    try:
        # Get all active owners
        owners = db.execute(
            select(models.Owner).where(models.Owner.is_active == True)
        ).scalars().all()
        
        print(f"🔍 Checking tax alerts for {len(owners)} active owner(s)...")
        
        for owner in owners:
            try:
                # Check if alert needs to be sent for this owner
                today = datetime.utcnow().date()
                deadline = get_current_quarter_deadline(today)
                days_until = (deadline - today).days
                
                # Send alert if 1 week (7 days) before deadline
                if 5 <= days_until <= 9:  # 1 week = 7 days, with 2 day window
                    print(f"📧 Sending 1-week tax alert to owner: {owner.email} (Order #{owner.id})")
                    # Import here to avoid circular dependency
                    from fastapi import BackgroundTasks
                    from .utils_email import send_email
                    from .routers_taxes import _quarter_bounds, calculate_commercial_tax
                    from . import crud
                    
                    background_tasks = BackgroundTasks()
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
                        <p><strong>Total Tax Due:</strong> ₹ {tax_info['total_tax']:,.2f}</p>
                        <p><strong>Payment Deadline:</strong> {deadline.strftime('%d %B %Y')}</p>
                        <p><strong>Days Remaining:</strong> {days_until} days (1 week)</p>
                        <p style='color: red; font-weight: bold; font-size: 16px;'>⚠️ Please make payment immediately to avoid penalties and late fees.</p>
                        <p style='margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;'>
                            <small>This is an automated reminder from Small Scale Business Automation system.</small>
                        </p>
                    </div>
                    """
                    
                    # Send email directly
                    from .utils_email import send_email
                    send_email(subject, owner.email, html)
                    print(f"✅ Tax alert sent to {owner.email}")
                    
            except Exception as e:
                print(f"❌ Error sending alert to owner {owner.email}: {str(e)}")
                continue
        
        print("✅ Tax alert check completed")
        
    except Exception as e:
        print(f"❌ Error in tax alert scheduler: {str(e)}")
    finally:
        db.close()


def run_daily_tax_check():
    """Synchronous wrapper for daily tax check."""
    try:
        asyncio.run(check_and_send_tax_alerts())
    except RuntimeError:
        # Already in event loop, create task
        asyncio.create_task(check_and_send_tax_alerts())

