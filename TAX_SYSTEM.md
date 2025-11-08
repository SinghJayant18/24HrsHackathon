# Tax System Documentation

## 📊 Tax Rate: 10% (Fixed)

**Both Taxes and Reports sections use the same 10% tax rate for consistency.**

### Calculation Formula:
```
Total Tax = Revenue × 10%
```

---

## 📅 Quarterly Tax Deadlines

Tax payment deadlines are on the **29th of every 3rd month**:
- **March 29** (Q1 deadline)
- **June 29** (Q2 deadline)
- **September 29** (Q3 deadline)
- **December 29** (Q4 deadline)

---

## 📧 Automated Email Alerts

### Alert Schedule:
1. **15 weeks before deadline** - Early reminder
2. **1 week before deadline** - URGENT reminder ⚠️

### Email Recipient:
- All tax alerts are sent to the **owner's registered email** (the email used during registration/login)

### Email Content:
- Quarter information
- Total revenue for the quarter
- Tax breakdown (10% rate)
- Total tax due
- Payment deadline date
- Days remaining
- Urgent warning (for 1-week alert)

---

## 🔄 Synchronization: Taxes & Reports

Both sections now use the **same 10% tax rate**:

### Taxes Section:
- Endpoint: `GET /taxes/quarterly-summary`
- Uses: `settings.total_tax_rate_percent` (10%)
- Calculation: `Revenue × 10%`

### Reports Section:
- Endpoint: `GET /reports/revenue/tax`
- Uses: `settings.total_tax_rate_percent` (10%)
- Calculation: `Revenue × 10%`

**✅ Both sections are now synchronized with 10% tax rate.**

---

## 🚀 Automated Alert Endpoints

### 1. Manual Check (Requires Login):
```
GET /taxes/check-alerts
```
- Checks if alerts need to be sent for logged-in owner
- Sends alerts if 15 weeks or 1 week before deadline

### 2. Automated Check (For Cron Jobs):
```
POST /taxes/auto-check-alerts
```
- Checks ALL active owners
- Sends automated emails to owners who are 1 week before deadline
- No authentication required (for automated systems)

---

## 📋 Setup Automated Daily Check

### Option 1: Cron Job (Linux/Mac)
Add to crontab:
```bash
# Run daily at 9 AM
0 9 * * * curl -X POST http://localhost:8000/taxes/auto-check-alerts
```

### Option 2: Scheduled Task (Windows)
Create a scheduled task to call:
```
POST http://localhost:8000/taxes/auto-check-alerts
```

### Option 3: Railway/Render Cron
In your deployment platform, set up a scheduled task to call the endpoint daily.

---

## 📊 Example Calculation

**Revenue:** ₹100,000
**Tax Rate:** 10%
**Total Tax Due:** ₹10,000

**Breakdown:**
- Tax (10%): ₹10,000

---

## ✅ Features Summary

- ✅ Fixed 10% tax rate (synchronized across Taxes & Reports)
- ✅ Quarterly deadlines (29th of every 3rd month)
- ✅ Automated email alerts 1 week before deadline
- ✅ Emails sent to owner's registered email
- ✅ Tax calculation consistent across all sections

---

## 🔧 Configuration

Tax rate can be changed in `.env`:
```env
TOTAL_TAX_RATE_PERCENT=10.0
```

**Note:** Changing this will update both Taxes and Reports sections automatically.

