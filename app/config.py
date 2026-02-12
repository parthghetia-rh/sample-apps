"""
Slot Sniper configuration.
Load from environment variables; use .env file for local development.
"""
import os
from dataclasses import dataclass
from typing import Optional

# Optional: load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class SlotTarget:
    """Target slot: date, time range, and location."""
    date: str          # e.g. "2025-02-15"
    time_start: str    # e.g. "19:00" (7 PM)
    time_end: str      # e.g. "21:00" (9 PM)
    location: str      # e.g. "Central Badminton Club"


@dataclass
class ScraperConfig:
    """Scraper / booking site settings."""
    booking_url: str
    check_interval_seconds: int = 60
    headless: bool = True
    # Optional: CSS selectors or XPath for your specific site (customize in .env or code)
    slot_container_selector: Optional[str] = None
    date_selector: Optional[str] = None
    time_selector: Optional[str] = None
    location_selector: Optional[str] = None


@dataclass
class TelegramConfig:
    """Telegram bot settings."""
    enabled: bool = True
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None


@dataclass
class EmailConfig:
    """Email (SMTP) settings for alerts."""
    enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_addr: str = ""
    to_addr: str = ""
    use_tls: bool = True


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key, default)


def get_slot_target() -> SlotTarget:
    return SlotTarget(
        date=_env("TARGET_DATE", "2025-02-15"),
        time_start=_env("TARGET_TIME_START", "19:00"),
        time_end=_env("TARGET_TIME_END", "21:00"),
        location=_env("TARGET_LOCATION", "Central Badminton Club"),
    )


def get_scraper_config() -> ScraperConfig:
    return ScraperConfig(
        booking_url=_env("BOOKING_URL", "https://example-booking-site.com/courts"),
        check_interval_seconds=int(_env("CHECK_INTERVAL_SECONDS", "60")),
        headless=_env("HEADLESS", "true").lower() == "true",
        slot_container_selector=_env("SLOT_CONTAINER_SELECTOR"),
        date_selector=_env("DATE_SELECTOR"),
        time_selector=_env("TIME_SELECTOR"),
        location_selector=_env("LOCATION_SELECTOR"),
    )


def get_telegram_config() -> TelegramConfig:
    token = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    return TelegramConfig(
        enabled=bool(token and chat_id),
        bot_token=token,
        chat_id=chat_id,
    )


def get_email_config() -> EmailConfig:
    return EmailConfig(
        enabled=bool(_env("SMTP_HOST") and _env("SMTP_USER") and _env("TO_EMAIL")),
        smtp_host=_env("SMTP_HOST", ""),
        smtp_port=int(_env("SMTP_PORT", "587")),
        smtp_user=_env("SMTP_USER", ""),
        smtp_password=_env("SMTP_PASSWORD", ""),
        from_addr=_env("FROM_EMAIL", _env("SMTP_USER", "")),
        to_addr=_env("TO_EMAIL", ""),
        use_tls=_env("SMTP_USE_TLS", "true").lower() == "true",
    )
