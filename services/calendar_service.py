import hashlib
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from database import (
    get_calendar_by_url,
    save_calendar,
    get_calendars,
)

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
    "Accept": ("text/html,application/xhtml+xml," "application/xml;q=0.9,*/*;q=0.8"),
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


def parse_calendars(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    results = []
    candidates = []

    for heading in soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]
    ):
        title = clean_text(
            heading.get_text(
                " ",
                strip=True,
            )
        )

        if not title:
            continue

        lowered = title.lower()

        if "trimester" not in lowered and "semester" not in lowered:
            continue

        parent = heading.parent

        if parent:
            candidates.append(
                (
                    heading,
                    title,
                    parent,
                )
            )

    for heading, title, parent in candidates:
        links = parent.find_all(
            "a",
            href=True,
        )

        if not links and parent.parent:
            links = parent.parent.find_all(
                "a",
                href=True,
            )

        page_url = None
        pdf_url = None

        for link in links:
            href = link.get(
                "href",
                "",
            ).strip()

            if not href:
                continue

            full_url = urljoin(
                CALENDAR_URL,
                href,
            )

            lower_url = full_url.lower()

            if ".pdf" in lower_url:
                pdf_url = full_url

            elif "/academics/calendar/" in lower_url:
                page_url = full_url

        url = page_url or pdf_url

        if not url:
            continue

        content = clean_text(
            parent.get_text(
                " ",
                strip=True,
            )
        )

        if len(content) < 20:
            continue

        content_hash = make_hash(title + "|" + content + "|" + url)

        results.append(
            {
                "title": title,
                "url": url,
                "content": content,
                "content_hash": content_hash,
            }
        )

    unique = {}

    for item in results:
        unique[item["url"]] = item

    return list(unique.values())


async def fetch_calendars():
    html = await fetch_calendar_page()

    return parse_calendars(html)


async def get_latest_calendars(
    limit=5,
):
    calendars = await fetch_calendars()

    if calendars:
        return calendars[:limit]

    rows = get_calendars(limit=limit)

    result = []

    for row in rows:
        result.append(
            {
                "id": row["id"],
                "title": row["title"],
                "url": row["url"],
                "content": row["content"] or "",
                "content_hash": row["content_hash"] or "",
            }
        )

    return result


async def sync_calendars():
    calendars = await fetch_calendars()

    new_items = []
    updated_items = []

    for calendar in calendars:
        existing = get_calendar_by_url(calendar["url"])

        if existing is None:
            save_calendar(
                calendar["title"],
                calendar["url"],
                calendar["content_hash"],
                calendar["content"],
            )

            new_items.append(calendar)

        elif existing["content_hash"] != calendar["content_hash"]:
            save_calendar(
                calendar["title"],
                calendar["url"],
                calendar["content_hash"],
                calendar["content"],
            )

            updated_items.append(calendar)

    return {
        "calendars": calendars,
        "new": new_items,
        "updated": updated_items,
    }
