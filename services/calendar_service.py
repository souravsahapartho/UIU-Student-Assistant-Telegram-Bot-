import hashlib
import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCKED_TERMS = (
    "news",
    "notice",
    "notices",
    "event",
    "events",
    "scholarship award list",
    "course enrollment",
    "orientation notice",
    "gymnasium",
    "seminar",
    "workshop",
    "spotlight",
    "download pdf",
    "view more",
    "print",
)


def clean_text(text):
    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def normalize_url(url):
    if not url:
        return ""

    url = url.strip()

    if url.startswith("//"):
        return "https:" + url

    if url.startswith("/"):
        return "https://www.uiu.ac.bd" + url

    return url


def normalize_title(title):
    title = clean_text(title)

    title = re.sub(
        r"\s+\d{4}$",
        "",
        title,
    )

    return title.strip()


def is_calendar_title(title):
    title = normalize_title(title)
    lower = title.lower()

    if not title:
        return False

    if any(term in lower for term in BLOCKED_TERMS):
        return False

    if not re.search(
        r"\b20\d{2}\b",
        title,
    ):
        return False

    calendar_terms = (
        "semester",
        "trimester",
        "b. pharm",
        "b pharm",
    )

    return any(term in lower for term in calendar_terms)


def extract_year(title):
    match = re.search(
        r"\b20\d{2}\b",
        title,
    )

    if match:
        return match.group(1)

    return ""


def make_id(title, url):
    value = f"{title.strip().lower()}|" f"{url.strip().lower()}"

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_link_title(link):
    title = clean_text(
        link.get_text(
            " ",
            strip=True,
        )
    )

    if title:
        return title

    image = link.find("img")

    if image:
        return clean_text(
            image.get(
                "alt",
                "",
            )
        )

    return ""


def get_parent_calendar_title(link):
    candidates = []

    current = link

    for _ in range(6):
        if not current:
            break

        text = clean_text(
            current.get_text(
                " ",
                strip=True,
            )
        )

        if text:
            candidates.append(text)

        current = current.parent

    for text in candidates:
        if is_calendar_title(text):
            return normalize_title(text)

    return ""


def extract_calendar_entries(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    entries = []
    seen = set()

    academic_heading = None

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
        text = clean_text(
            heading.get_text(
                " ",
                strip=True,
            )
        )

        if text.lower() == "academic calendar":
            academic_heading = heading
            break

    links = soup.find_all(
        "a",
        href=True,
    )

    for link in links:
        href = normalize_url(
            link.get(
                "href",
                "",
            )
        )

        if not href:
            continue

        if "/academics/calendar/" not in href:
            continue

        if href.rstrip("/") == CALENDAR_URL.rstrip("/"):
            continue

        title = get_link_title(link)

        if not is_calendar_title(title):
            title = get_parent_calendar_title(link)

        if not title:
            continue

        title = normalize_title(title)

        if not is_calendar_title(title):
            continue

        if any(
            x in href.lower()
            for x in (
                "#",
                "javascript:",
            )
        ):
            continue

        key = href.rstrip("/").lower()

        if key in seen:
            continue

        seen.add(key)

        entries.append(
            {
                "id": make_id(
                    title,
                    href,
                ),
                "title": title,
                "url": href,
                "year": extract_year(
                    title,
                ),
            }
        )

    if not entries and academic_heading:
        section_text = clean_text(
            academic_heading.parent.get_text(
                " ",
                strip=True,
            )
        )

        logger.warning(
            "Academic Calendar section found but no links extracted. Text: %s",
            section_text[:1000],
        )

    return entries


async def fetch_calendars():
    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=30,
        follow_redirects=True,
    ) as client:

        response = await client.get(CALENDAR_URL)

        response.raise_for_status()

        return extract_calendar_entries(response.text)


async def get_latest_calendars(
    limit=5,
):
    calendars = await fetch_calendars()

    return calendars[:limit]


async def get_all_calendars():
    return await fetch_calendars()
