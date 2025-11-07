import asyncio
import logging
from email.message import EmailMessage

import aiosmtplib

from .settings import settings


logger = logging.getLogger(__name__)


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
