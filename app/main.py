"""
Slot Sniper – monitor a booking site and get Telegram/Email alerts
when a slot in your preferred date, time, and location becomes available.

Usage:
  Set env vars (or .env) – see .env.example. Then:
    python -m app.main

  Demo mode (no real site, optional test alert):
    DEMO_MODE=1 python -m app.main
"""
import logging
import os
import sys
import time
from typing import List

from app.config import (
    get_email_config,
    get_scraper_config,
    get_slot_target,
    get_telegram_config,
)
from app.notifier import notify_slots_found
from app.scraper import Slot, fetch_available_slots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_demo_slots(target_date: str, target_time_start: str, target_time_end: str, location: str) -> List[Slot]:
    """Return fake available slots for testing (DEMO_MODE=1)."""
    return [
        Slot(
            date=target_date,
            time_start=target_time_start,
            time_end=target_time_end,
            location=location,
            raw_text="Demo slot",
        ),
    ]


def run_once(
    target_date: str,
    target_time_start: str,
    target_time_end: str,
    target_location: str,
    booking_url: str,
    headless: bool,
    slot_container_selector: str | None,
    date_selector: str | None,
    time_selector: str | None,
    location_selector: str | None,
    demo_mode: bool,
) -> List[Slot]:
    """Fetch slots and return those matching the target."""
    if demo_mode:
        logger.info("Demo mode: using mock slots")
        all_slots = get_demo_slots(target_date, target_time_start, target_time_end, target_location)
    else:
        try:
            all_slots = fetch_available_slots(
                url=booking_url,
                headless=headless,
                slot_container_selector=slot_container_selector,
                date_selector=date_selector,
                time_selector=time_selector,
                location_selector=location_selector,
                use_playwright=True,
            )
        except Exception as e:
            logger.exception("Scrape failed: %s", e)
            return []
    matching = [
        s for s in all_slots
        if s.matches(target_date, target_time_start, target_time_end, target_location)
    ]
    return matching


def main() -> None:
    demo_mode = os.environ.get("DEMO_MODE", "").strip().lower() in ("1", "true", "yes")
    target = get_slot_target()
    scraper_cfg = get_scraper_config()
    telegram_cfg = get_telegram_config()
    email_cfg = get_email_config()

    if not telegram_cfg.enabled and not email_cfg.enabled:
        logger.warning("No notifications configured. Set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID or SMTP_* for email.")

    logger.info(
        "Slot Sniper started – target: %s %s–%s @ %s",
        target.date,
        target.time_start,
        target.time_end,
        target.location,
    )
    if demo_mode:
        logger.info("Running in DEMO_MODE – use real BOOKING_URL and unset DEMO_MODE for production")

    interval = scraper_cfg.check_interval_seconds
    while True:
        try:
            matching = run_once(
                target_date=target.date,
                target_time_start=target.time_start,
                target_time_end=target.time_end,
                target_location=target.location,
                booking_url=scraper_cfg.booking_url,
                headless=scraper_cfg.headless,
                slot_container_selector=scraper_cfg.slot_container_selector,
                date_selector=scraper_cfg.date_selector,
                time_selector=scraper_cfg.time_selector,
                location_selector=scraper_cfg.location_selector,
                demo_mode=demo_mode,
            )
            if matching:
                logger.info("Target slot(s) found: %s", matching)
                notify_slots_found(
                    slots=matching,
                    booking_url=scraper_cfg.booking_url,
                    telegram_token=telegram_cfg.bot_token,
                    telegram_chat_id=telegram_cfg.chat_id,
                    email_config=email_cfg,
                )
                # Optional: exit after first alert; comment out to keep monitoring
                # logger.info("Exiting after first alert.")
                # break
            else:
                logger.debug("No matching slots this run.")
        except KeyboardInterrupt:
            logger.info("Stopped by user")
            break
        except Exception as e:
            logger.exception("Loop error: %s", e)

        logger.info("Next check in %s seconds", interval)
        time.sleep(interval)


if __name__ == "__main__":
    main()
    sys.exit(0)
