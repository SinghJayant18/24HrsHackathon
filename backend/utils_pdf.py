from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def generate_revenue_report_pdf(period_label: str, revenue: float, details: list[tuple[str, float]] | None = None) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, f"Revenue Report - {period_label}")
    y -= 1.2 * cm
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, y, f"Total Revenue: ₹ {revenue:,.2f}")
    y -= 1.0 * cm
    if details:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Breakdown:")
        y -= 0.8 * cm
        c.setFont("Helvetica", 11)
        for label, amt in details:
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 11)
            c.drawString(2.5 * cm, y, f"- {label}: ₹ {amt:,.2f}")
            y -= 0.6 * cm
    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf


def generate_ebill_pdf(order_data: dict) -> bytes:
    """Generate downloadable e-bill PDF for order."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "E-BILL / INVOICE")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Order ID: #{order_data.get('id', 'N/A')}")
    y -= 0.6 * cm
    created_at = order_data.get("created_at", "")
    if isinstance(created_at, str):
        c.drawString(2 * cm, y, f"Date: {created_at}")
    else:
        c.drawString(2 * cm, y, f"Date: {created_at.strftime('%Y-%m-%d %H:%M') if hasattr(created_at, 'strftime') else 'N/A'}")
    y -= 1.5 * cm

    # Customer Details
    customer = order_data.get("customer", {})
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Bill To:")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, customer.get("name", ""))
    y -= 0.5 * cm
    c.drawString(2 * cm, y, customer.get("email", ""))
    y -= 0.5 * cm
    if customer.get("address"):
        c.drawString(2 * cm, y, customer.get("address", ""))
        y -= 0.5 * cm
    if customer.get("phone"):
        c.drawString(2 * cm, y, f"Phone: {customer.get('phone', '')}")
        y -= 1.0 * cm

    # Items Table Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "Item")
    c.drawString(8 * cm, y, "Qty")
    c.drawString(10 * cm, y, "Price")
    c.drawString(13 * cm, y, "Disc%")
    c.drawString(15 * cm, y, "Total")
    y -= 0.6 * cm
    c.line(2 * cm, y, 18 * cm, y)
    y -= 0.4 * cm

    # Items
    c.setFont("Helvetica", 9)
    items = order_data.get("items", [])
    subtotal = 0.0
    total_discount = 0.0
    
    for item in items:
        item_name = item.get("item", {}).get("name", f"Item {item.get('item_id')}")
        qty = item.get("quantity", 0)
        price_at_purchase = item.get("price_at_purchase", 0.0)  # Already discounted
        discount_pct = item.get("item", {}).get("discount_percent", 0.0)
        
        # Calculate original price before discount
        if discount_pct > 0:
            original_price = price_at_purchase / (1 - discount_pct / 100.0)
        else:
            original_price = price_at_purchase
        
        # Calculate totals
        item_subtotal = original_price * qty
        item_discount = item_subtotal * (discount_pct / 100.0)
        item_total = price_at_purchase * qty  # Final after discount
        
        subtotal += item_subtotal
        total_discount += item_discount

        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm

        c.drawString(2 * cm, y, item_name[:30])
        c.drawString(8 * cm, y, str(qty))
        c.drawString(10 * cm, y, f"₹{price_at_purchase:.2f}")
        c.drawString(13 * cm, y, f"{discount_pct}%")
        c.drawString(15 * cm, y, f"₹{item_total:.2f}")
        y -= 0.5 * cm

    y -= 0.3 * cm
    c.line(2 * cm, y, 18 * cm, y)
    y -= 0.5 * cm

    # Bill Summary
    taxable_amount = subtotal - total_discount
    tax_rate = 18.0  # Default 18% GST
    tax_amt = taxable_amount * (tax_rate / 100.0)
    sgst = tax_amt / 2
    cgst = tax_amt / 2
    final_total = taxable_amount + tax_amt  # Subtotal - Discount + Tax

    c.setFont("Helvetica", 10)
    c.drawString(12 * cm, y, "Subtotal:")
    c.drawString(15 * cm, y, f"₹{subtotal:.2f}")
    y -= 0.5 * cm
    if total_discount > 0:
        c.drawString(12 * cm, y, "Discount:")
        c.drawString(15 * cm, y, f"-₹{total_discount:.2f}")
        y -= 0.5 * cm
    c.drawString(12 * cm, y, "CGST (9%):")
    c.drawString(15 * cm, y, f"₹{cgst:.2f}")
    y -= 0.5 * cm
    c.drawString(12 * cm, y, "SGST (9%):")
    c.drawString(15 * cm, y, f"₹{sgst:.2f}")
    y -= 0.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(12 * cm, y, "Total Amount:")
    c.drawString(15 * cm, y, f"₹{final_total:.2f}")
    y -= 1.0 * cm

    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, y, "Thank you for your order!")
    y -= 0.4 * cm
    status = order_data.get("status", "N/A")
    if isinstance(status, str):
        c.drawString(2 * cm, y, f"Order Status: {status.upper()}")
    else:
        c.drawString(2 * cm, y, f"Order Status: {status.value.upper() if hasattr(status, 'value') else 'N/A'}")

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf

