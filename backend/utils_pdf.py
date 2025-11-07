from io import BytesIO
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

