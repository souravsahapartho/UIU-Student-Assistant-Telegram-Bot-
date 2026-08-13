import hashlib
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
    "Accept": ("text/html,application/xhtml+xml," "application/xml;q=0.9," "*/*;q=0.8"),
    "Accept-Language": "en-US,en;q=0.9",
}


def clean_text(text):
    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def make_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_calendar_url(url):
    if not url:
        return False

    normalized = url.rstrip("/").lower()
    archive = CALENDAR_URL.rstrip("/").lower()

    if normalized == archive:
        return False

    return "/academics/calendar/" in normalized


def is_valid_calendar_title(title):
    title = clean_text(title)

    if not title:
        return False

    lower = title.lower()

    if "semester" not in lower and "trimester" not in lower:
        return False

    if not re.search(
        r"\b20\d{2}\b",
        title,
    ):
        return False

    blocked = [
        "notice",
        "notices",
        "event",
        "events",
        "scholarship award",
        "course enrollment",
        "orientation notice",
        "download pdf",
        "view calendar",
    ]

    for word in blocked:
        if word in lower:
            return False

    return True


def extract_year(title):
    match = re.search(
        r"\b20\d{2}\b",
        title,
    )

    if match:
        return match.group(0)

    return ""


def normalize_title(title):
    title = clean_text(title)

    title = re.sub(
        r"\s*\[Revised\]\s*$",
        " [Revised]",
        title,
        flags=re.IGNORECASE,
    )

    return title


def parse_calendar_archive(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    calendars = []
    seen_urls = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = clean_text(
            link.get(
                "href",
                "",
            )
        )

        if not href:
            continue

        url = urljoin(
            CALENDAR_URL,
            href,
        )

        if not is_calendar_url(url):
            continue

        title = clean_text(
            link.get_text(
                " ",
                strip=True,
            )
        )

        if not title:
            title = clean_text(
                link.get(
                    "title",
                    "",
                )
            )

        if not title:
            continue

        title = normalize_title(title)

        if not is_valid_calendar_title(title):
            continue

        normalized_url = url.rstrip("/").lower()

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)

        calendars.append(
            {
                "title": title,
                "url": url,
                "year": extract_year(title),
                "content": "",
                "content_hash": make_hash(title + "|" + url),
            }
        )

    return calendars


async def fetch_calendar_page():
    timeout = httpx.Timeout(
        30.0,
        connect=15.0,
    )

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=timeout,
        follow_redirects=True,
    ) as client:
        response = await client.get(CALENDAR_URL)

        response.raise_for_status()

        return response.text


async def fetch_calendars():
    html = await fetch_calendar_page()

    calendars = parse_calendar_archive(html)

    return calendars[:5]


async def get_latest_calendars(
    limit=5,
):
    calendars = await fetch_calendars()

    return calendars[:limit]
