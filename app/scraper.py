"""
Slot Sniper – web scraping with Playwright and BeautifulSoup.
Fetches the booking page and parses available slots. Customize parse_slots_from_html()
for your actual booking site's structure.
"""
import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class Slot:
    """A single bookable slot."""
    date: str
    time_start: str
    time_end: str
    location: str
    raw_text: str = ""

    def matches(self, target_date: str, target_time_start: str, target_time_end: str, target_location: str) -> bool:
        """Check if this slot matches the user's target filters."""
        date_ok = self.date == target_date
        location_ok = (not target_location) or (target_location.lower() in self.location.lower())
        # Normalize times for comparison (e.g. "19:00" vs "7:00 PM")
        t_start = _normalize_time(self.time_start)
        t_end = _normalize_time(self.time_end)
        tr_start = _normalize_time(target_time_start)
        tr_end = _normalize_time(target_time_end)
        time_ok = t_start == tr_start and t_end == tr_end
        return date_ok and location_ok and time_ok


def _normalize_time(t: str) -> str:
    """Convert various time formats to HH:MM (24h)."""
    if not t:
        return ""
    t = t.strip()
    # Already HH:MM or H:MM
    m = re.match(r"(\d{1,2}):(\d{2})", t)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        return f"{h:02d}:{mi:02d}"
    # 7 PM / 7pm
    m = re.match(r"(\d{1,2})\s*(am|pm)", t, re.I)
    if m:
        h, ampm = int(m.group(1)), m.group(2).lower()
        if ampm == "pm" and h != 12:
            h += 12
        elif ampm == "am" and h == 12:
            h = 0
        return f"{h:02d}:00"
    return t


def get_page_html(url: str, headless: bool = True) -> str:
    """
    Load the booking URL with Playwright and return the page HTML.
    Use this when the site is JavaScript-heavy; otherwise requests + BeautifulSoup is enough.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("Install playwright: pip install playwright && playwright install chromium")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)  # allow any JS-rendered content
            html = page.content()
        finally:
            browser.close()
    return html


def parse_slots_from_html(
    html: str,
    slot_container_selector: Optional[str] = None,
    date_selector: Optional[str] = None,
    time_selector: Optional[str] = None,
    location_selector: Optional[str] = None,
) -> List[Slot]:
    """
    Parse the booking page HTML into a list of Slot objects.
    Customize this for your actual site: inspect the page and set selectors
    (or use different logic). This default implementation looks for common patterns.
    """
    soup = BeautifulSoup(html, "html.parser")
    slots: List[Slot] = []

    # If you have a container for each slot (e.g. .slot-card), use it
    if slot_container_selector:
        containers = soup.select(slot_container_selector)
        for el in containers:
            date_el = el.select_one(date_selector) if date_selector else None
            time_el = el.select_one(time_selector) if time_selector else None
            loc_el = el.select_one(location_selector) if location_selector else None
            slot = _slot_from_elements(date_el, time_el, loc_el, el.get_text(strip=True))
            if slot:
                slots.append(slot)
        return slots

    # Fallback: try to find table rows or list items that look like slots
    for table in soup.find_all("table"):
        for row in table.find_all("tr")[1:]:  # skip header
            cells = row.find_all(["td", "th"])
            if len(cells) >= 3:
                slot = _slot_from_cells(cells)
                if slot:
                    slots.append(slot)

    # List of cards/divs with data attributes
    for el in soup.find_all(attrs={"data-date": True}):
        date = el.get("data-date", "")
        time_range = el.get("data-time", "") or el.get("data-time-range", "")
        loc = el.get("data-location", "") or el.get("data-venue", "")
        if date or time_range or loc:
            start, end = _parse_time_range(time_range)
            slots.append(Slot(date=date, time_start=start, time_end=end, location=loc, raw_text=el.get_text(strip=True)))

    return slots


def _slot_from_elements(
    date_el: Optional[object],
    time_el: Optional[object],
    loc_el: Optional[object],
    raw: str,
) -> Optional[Slot]:
    if not date_el and not time_el:
        return None
    date = date_el.get_text(strip=True) if date_el else ""
    time_text = time_el.get_text(strip=True) if time_el else ""
    loc = loc_el.get_text(strip=True) if loc_el else ""
    start, end = _parse_time_range(time_text)
    return Slot(date=date, time_start=start, time_end=end, location=loc, raw_text=raw)


def _slot_from_cells(cells: list) -> Optional[Slot]:
    texts = [c.get_text(strip=True) for c in cells]
    if len(texts) < 2:
        return None
    # Heuristic: first column date, second time, third location
    date = texts[0] if len(texts) > 0 else ""
    time_text = texts[1] if len(texts) > 1 else ""
    loc = texts[2] if len(texts) > 2 else ""
    start, end = _parse_time_range(time_text)
    return Slot(date=date, time_start=start, time_end=end, location=loc, raw_text=" | ".join(texts))


def _parse_time_range(s: str) -> tuple:
    """Parse '19:00 - 21:00' or '7 PM - 9 PM' into (start, end)."""
    if not s:
        return "", ""
    s = s.strip()
    if "-" in s:
        parts = s.split("-", 1)
        return _normalize_time(parts[0].strip()), _normalize_time(parts[1].strip())
    if "–" in s:
        parts = s.split("–", 1)
        return _normalize_time(parts[0].strip()), _normalize_time(parts[1].strip())
    return _normalize_time(s), ""


def fetch_available_slots(
    url: str,
    headless: bool = True,
    slot_container_selector: Optional[str] = None,
    date_selector: Optional[str] = None,
    time_selector: Optional[str] = None,
    location_selector: Optional[str] = None,
    use_playwright: bool = True,
) -> List[Slot]:
    """
    Fetch the booking page and return all parsed slots.
    Set use_playwright=False to only parse HTML you provide (e.g. from requests).
    """
    if use_playwright:
        html = get_page_html(url, headless=headless)
    else:
        import urllib.request
        with urllib.request.urlopen(url) as resp:
            html = resp.read().decode()
    return parse_slots_from_html(
        html,
        slot_container_selector=slot_container_selector,
        date_selector=date_selector,
        time_selector=time_selector,
        location_selector=location_selector,
    )
