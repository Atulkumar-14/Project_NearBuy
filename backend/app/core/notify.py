import logging
from app.core.config import settings


def send_email(to: str, subject: str, body: str) -> None:
    # Stubbed email sender; integrate SMTP provider as needed
    logging.info(f"[EMAIL] to={to} subject={subject} body_len={len(body)}")


def send_sms(to: str, body: str) -> None:
    # Stubbed SMS sender; integrate Twilio or similar
    logging.info(f"[SMS] to={to} body_len={len(body)}")