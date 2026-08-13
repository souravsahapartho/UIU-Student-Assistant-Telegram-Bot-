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
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,"
        "image/avif,image/webp,"
        "*/*;q=0.8"
    ),
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


def is_calendar_title(title):
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
        "news",
        "event",
        "events",
        "scholarship award",
        "course enrollment",
        "orientation",
        "workshop",
        "seminar",
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


def find_calendar_url(element):
    candidates = []

    current = element

    for _ in range(6):
        if current is None:
            break

        candidates.extend(
            current.find_all(
                "a",
                href=True,
            )
        )

        current = current.parent

    seen = set()

    for link in candidates:
        href = clean_text(
            link.get(
                "href",
                "",
            )
        )

        if not href:
            continue

        full_url = urljoin(
            CALENDAR_URL,
            href,
        )

        if full_url in seen:
            continue

        seen.add(full_url)

        lower = full_url.lower()

        if ".pdf" in lower or "/academics/calendar/" in lower:
            if full_url.rstrip("/") != CALENDAR_URL.rstrip("/"):
                return full_url

    return ""


def extract_title_from_element(element):
    text = clean_text(
        element.get_text(
            " ",
            strip=True,
        )
    )

    if is_calendar_title(text):
        return text

    for child in element.find_all(
        [
            "div",
            "span",
            "p",
            "strong",
            "b",
            "a",
        ]
    ):
        child_text = clean_text(
            child.get_text(
                " ",
                strip=True,
            )
        )

        if is_calendar_title(child_text):
            return child_text

    return ""


def parse_calendar_page(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    results = []
    seen = set()

    all_elements = soup.find_all(True)

    for element in all_elements:
        text = extract_title_from_element(element)

        if not text:
            continue

        if not is_calendar_title(text):
            continue

        url = find_calendar_url(element)

        if not url:
            continue

        key = (
            text.lower().strip(),
            url.lower().strip(),
        )

        if key in seen:
            continue

        seen.add(key)

        content = clean_text(
            element.get_text(
                " ",
                strip=True,
            )
        )

        results.append(
            {
                "title": text,
                "url": url,
                "year": extract_year(text),
                "content": content,
                "content_hash": make_hash(text + "|" + url + "|" + content),
            }
        )

    return results


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

    calendars = parse_calendar_page(html)

    unique = []
    seen_urls = set()

    for calendar in calendars:
        url = calendar["url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique.append(calendar)

    return unique


async def get_latest_calendars(
    limit=5,
):
    calendars = await fetch_calendars()

    return calendars[:limit]
