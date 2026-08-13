import re
import httpx
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0 Safari/537.36"
}

CALENDAR_PATTERN = re.compile(
    r"\b(20\d{2})\b.*\b(" r"semester|trimester|b\.?\s*pharm|calendar" r")\b",
    re.IGNORECASE,
)


def clean_text(text):
    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def is_calendar_title(title):
    title = clean_text(title)

    if not title:
        return False

    lower = title.lower()

    blocked = [
        "notice",
        "news",
        "event",
        "scholarship award",
        "course enrollment",
        "orientation notice",
        "online class",
        "gymnasium",
        "admission test",
        "seminar",
        "workshop",
        "spotlight",
    ]

    if any(item in lower for item in blocked):
        return False

    if not re.search(
        r"\b20\d{2}\b",
        title,
    ):
        return False

    keywords = [
        "semester",
        "trimester",
        "b. pharm",
        "b pharm",
    ]

    return any(keyword in lower for keyword in keywords)


def extract_year(title):
    match = re.search(
        r"\b(20\d{2})\b",
        title,
    )

    if match:
        return match.group(1)

    return ""


def normalize_url(url):
    if not url:
        return ""

    url = url.strip()

    if url.startswith("//"):
        return "https:" + url

    if url.startswith("/"):
        return "https://www.uiu.ac.bd" + url

    return url


def extract_calendar_entries(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    entries = []
    seen = set()

    candidates = []

    for tag in soup.find_all(["a", "h2", "h3", "h4", "h5"]):
        title = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not title:
            continue

        if not is_calendar_title(title):
            continue

        link = ""

        if tag.name == "a":
            link = tag.get("href", "")
        else:
            parent_link = tag.find_parent("a")

            if parent_link:
                link = parent_link.get(
                    "href",
                    "",
                )

            if not link:
                next_link = tag.find_next("a")

                if next_link:
                    href = next_link.get(
                        "href",
                        "",
                    )

                    if href:
                        link = href

        link = normalize_url(link)

        if not link:
            continue

        if "/academics/calendar/" not in link:
            continue

        if link.rstrip("/") == CALENDAR_URL.rstrip("/"):
            continue

        key = (
            title.lower(),
            link.lower(),
        )

        if key in seen:
            continue

        seen.add(key)

        candidates.append(
            {
                "title": title,
                "url": link,
                "year": extract_year(title),
            }
        )

    entries.extend(candidates)

    return entries


async def fetch_calendars():
    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=20,
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


async def sync_calendars():
    current = await fetch_calendars()

    current = current[:50]

    return {
        "new": [],
        "updated": [],
        "calendars": current,
    }
