"""
Slot Sniper – push notifications via Telegram and/or Email.
"""
import logging
from typing import List, Optional

from app.scraper import Slot

logger = logging.getLogger(__name__)


def send_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API."""
    if not bot_token or not chat_id:
        logger.warning("Telegram not configured (missing token or chat_id)")
        return False
    try:
        import urllib.request
        import urllib.parse
        import json
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            ok = result.get("ok") is True
            if not ok:
                logger.error("Telegram API error: %s", result)
            return ok
    except Exception as e:
        logger.exception("Telegram send failed: %s", e)
        return False


def send_email_smtp(
    smtp_host: str,
    smtp_port: int,
    user: str,
    password: str,
    from_addr: str,
    to_addr: str,
    subject: str,
    body: str,
    use_tls: bool = True,
) -> bool:
    """Send an email via SMTP."""
    if not smtp_host or not user or not to_addr:
        logger.warning("Email not fully configured")
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_tls:
                server.starttls()
            if user and password:
                server.login(user, password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        logger.info("Email sent to %s", to_addr)
        return True
    except Exception as e:
        logger.exception("Email send failed: %s", e)
        return False


def format_slots_message(slots: List[Slot], booking_url: str = "") -> str:
    """Format a list of slots into a readable message for Telegram/Email."""
    lines = ["<b>Slot Sniper – target slot available!</b>", ""]
    for s in slots:
        lines.append(f"📅 {s.date}  |  {s.time_start}–{s.time_end}  |  {s.location}")
    if booking_url:
        lines.append("")
        lines.append(f"Book now: {booking_url}")
    return "\n".join(lines)


def notify_slots_found(
    slots: List[Slot],
    booking_url: str,
    telegram_token: Optional[str],
    telegram_chat_id: Optional[str],
    email_config: object | None,
) -> None:
    """
    Send push notifications for the given slots via Telegram and/or Email.
    email_config should have: smtp_host, smtp_port, smtp_user, smtp_password,
    from_addr, to_addr, use_tls (optional).
    """
    message = format_slots_message(slots, booking_url)
    # Plain text version for email
    plain = message.replace("<b>", "").replace("</b>", "")

    if telegram_token and telegram_chat_id:
        send_telegram(telegram_token, telegram_chat_id, message)

    if email_config and getattr(email_config, "enabled", False):
        send_email_smtp(
            smtp_host=getattr(email_config, "smtp_host", ""),
            smtp_port=getattr(email_config, "smtp_port", 587),
            user=getattr(email_config, "smtp_user", ""),
            password=getattr(email_config, "smtp_password", ""),
            from_addr=getattr(email_config, "from_addr", ""),
            to_addr=getattr(email_config, "to_addr", ""),
            subject="Slot Sniper: Target slot available!",
            body=plain,
            use_tls=getattr(email_config, "use_tls", True),
        )
