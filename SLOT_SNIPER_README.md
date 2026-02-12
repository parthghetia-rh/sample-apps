# Slot Sniper

A small Python app that monitors a badminton (or similar) court booking site and sends **Telegram** and/or **Email** alerts when a slot in your preferred date, time, and location becomes available.

## Features

- **Web scraping** with Playwright (JS-heavy sites) and BeautifulSoup (parsing)
- **Filter by** date, time range, and location
- **Push notifications** via Telegram and/or SMTP email when a target slot is found
- **Configurable** via environment variables or a `.env` file
- **Demo mode** to test alerts without a real booking URL

## Setup

1. **Create a virtualenv and install dependencies**

   ```bash
   cd sample-apps
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure**

   Copy `.env.example` to `.env` and fill in:

   - **Target slot**: `TARGET_DATE`, `TARGET_TIME_START`, `TARGET_TIME_END`, `TARGET_LOCATION`
   - **Booking site**: `BOOKING_URL`, optional `CHECK_INTERVAL_SECONDS`, `HEADLESS`
   - **Telegram**: create a bot with [@BotFather](https://t.me/BotFather), get token; get your `TELEGRAM_CHAT_ID` (e.g. from [@userinfobot](https://t.me/userinfobot))
   - **Email** (optional): SMTP settings (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `TO_EMAIL`, etc.)

3. **Customize the scraper for your site**

   The parser in `app/scraper.py` (`parse_slots_from_html`) is generic. For your actual booking site:

   - Open the booking page in the browser and inspect the HTML.
   - Set optional env vars: `SLOT_CONTAINER_SELECTOR`, `DATE_SELECTOR`, `TIME_SELECTOR`, `LOCATION_SELECTOR` (CSS selectors), **or**
   - Edit `parse_slots_from_html()` in `app/scraper.py` to use the correct tags/classes/attributes for your site.

## Run

- **Production** (real booking URL, real checks):

  ```bash
  python -m app.main
  ```

- **Demo** (mock slot, test Telegram/Email only):

  ```bash
  DEMO_MODE=1 python -m app.main
  ```

The script runs in a loop: it checks the site every `CHECK_INTERVAL_SECONDS`, filters slots by your target date/time/location, and sends notifications when a match is found. Stop with `Ctrl+C`.

## Project layout

- `app/main.py` – entrypoint and monitoring loop
- `app/config.py` – load settings from env / `.env`
- `app/scraper.py` – Playwright + BeautifulSoup: fetch page, parse slots
- `app/notifier.py` – Telegram (Bot API) and SMTP email alerts
- `.env.example` – example env vars; copy to `.env`

## Tools used

- **Playwright** – headless browser to load the booking page (handles JavaScript).
- **BeautifulSoup** – parse HTML and extract slot info.
- **Telegram** – Bot API (no extra library required; optional: `python-telegram-bot` for more features).
- **SMTP** – standard library for email.

## Notes

- Keep `TELEGRAM_BOT_TOKEN` and SMTP credentials in `.env`; do not commit `.env`.
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your normal password.
- Booking sites may change their HTML; if alerts stop working, re-inspect the page and update selectors or `parse_slots_from_html()`.
