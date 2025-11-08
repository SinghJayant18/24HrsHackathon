import asyncio
import logging
import ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import aiosmtplib

from .settings import settings


logger = logging.getLogger(__name__)

# Create SSL context that doesn't verify certificates (for development/demo)
# WARNING: Not secure for production!
_unverified_ssl_context = ssl.create_default_context()
_unverified_ssl_context.check_hostname = False
_unverified_ssl_context.verify_mode = ssl.CERT_NONE


async def send_email_async(
    subject: str,
    to_email: str,
    body_html: str,
    body_text: str | None = None,
) -> None:
    msg = EmailMessage()
    msg["From"] = settings.email_from or settings.smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text or "")
    msg.add_alternative(body_html, subtype="html")
    if not settings.smtp_username or not settings.smtp_password:
        logger.info(
            "SMTP not configured; capturing email locally",
            extra={
                "subject": subject,
                "to": to_email,
            },
        )
        print("\n--- EMAIL (mock send) ---")
        print(f"To      : {to_email}")
        print(f"Subject : {subject}")
        if body_text:
            print(f"Text    : {body_text}")
        print("HTML    :")
        print(body_html)
        print("--- END EMAIL ---\n")
        return
    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
        timeout=30,
        tls_context=_unverified_ssl_context,
    )


def send_email(
    subject: str,
    to_email: str,
    body_html: str,
    body_text: str | None = None,
) -> None:
    try:
        asyncio.run(send_email_async(subject, to_email, body_html, body_text))
    except RuntimeError:
        # already in loop (e.g., FastAPI), schedule a task
        asyncio.create_task(
            send_email_async(subject, to_email, body_html, body_text)
        )


async def send_email_with_pdf_async(
    subject: str,
    to_email: str,
    body_html: str,
    pdf_data: bytes,
    pdf_filename: str,
    body_text: str | None = None,
) -> None:
    """Send email with PDF attachment."""
    msg = MIMEMultipart()
    msg["From"] = settings.email_from or settings.smtp_username
    msg["To"] = to_email
    msg["Subject"] = subject

    if body_text:
        msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    # Attach PDF
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_data)
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f'attachment; filename="{pdf_filename}"'
    )
    msg.attach(part)

    if not settings.smtp_username or not settings.smtp_password:
        print("\n--- EMAIL WITH PDF (mock send) ---")
        print(f"To      : {to_email}")
        print(f"Subject : {subject}")
        print(f"PDF     : {pdf_filename} ({len(pdf_data)} bytes)")
        print("HTML    :")
        print(body_html)
        print("--- END EMAIL ---\n")
        return

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        start_tls=True,
        username=settings.smtp_username,
        password=settings.smtp_password,
        timeout=30,
        tls_context=_unverified_ssl_context,
    )


def send_email_with_pdf(
    subject: str,
    to_email: str,
    body_html: str,
    pdf_data: bytes,
    pdf_filename: str,
    body_text: str | None = None,
) -> None:
    """Send email with PDF attachment (synchronous wrapper)."""
    try:
        # Check if SMTP is configured
        if not settings.smtp_username or not settings.smtp_password:
            print(f"\n⚠️  EMAIL NOT SENT - SMTP not configured!")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Configure SMTP_USERNAME and SMTP_PASSWORD in .env file")
            print("---\n")
            return

        # Try to send email
        try:
            asyncio.run(
                send_email_with_pdf_async(
                    subject, to_email, body_html, pdf_data, pdf_filename, body_text
                )
            )
            print(f"✅ Email sent successfully to {to_email}")
        except RuntimeError:
            # Already in event loop, use create_task
            asyncio.create_task(
                send_email_with_pdf_async(
                    subject, to_email, body_html, pdf_data, pdf_filename, body_text
                )
            )
            print(f"✅ Email queued for {to_email}")
        except Exception as e:
            print(f"❌ Email sending failed to {to_email}: {str(e)}")
            logger.error(f"Email send error: {e}", exc_info=True)
    except Exception as e:
        print(f"❌ Email function error: {str(e)}")
        logger.error(f"Email function error: {e}", exc_info=True)
