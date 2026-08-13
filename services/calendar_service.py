import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}

CALENDAR_TITLE_PATTERNS = [
    r"\b\d{4}\b.*semester",
    r"\b\d{4}\b.*trimester",
    r"\b\d{4}\b.*b\.?\s*pharm",
    r"\b\d{4}\b.*b pharm",
]

BLOCKED_TERMS = [
    "news",
    "notice",
    "notices",
    "event",
    "events",
    "scholarship award",
    "course enrollment",
    "gymnasium",
    "orientation notice",
    "seminar",
    "workshop",
    "spotlight",
    "download pdf",
    "view more",
]


def clean_text(text):
    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def normalize_title(title):
    title = clean_text(title)

    title = title.replace(
        "\xa0",
        " ",
    )

    title = re.sub(
        r"\s+",
        " ",
        title,
    )

    return title.strip()


def is_calendar_title(title):
    title = normalize_title(title)

    if not title:
        return False

    lower = title.lower()

    if any(term in lower for term in BLOCKED_TERMS):
        return False

    if not re.search(
        r"\b20\d{2}\b",
        title,
    ):
        return False

    for pattern in CALENDAR_TITLE_PATTERNS:
        if re.search(
            pattern,
            lower,
        ):
            return True

    return False


def slugify(text):
    text = normalize_title(text)

    text = text.replace(
        "[Revised]",
        " revised",
    )

    text = text.replace(
        "[revised]",
        " revised",
    )

    text = text.replace(
        "&",
        " and ",
    )

    text = text.replace(
        "/",
        " ",
    )

    text = text.replace(
        "(",
        " ",
    )

    text = text.replace(
        ")",
        " ",
    )

    text = text.replace(
        ".",
        "",
    )

    text = re.sub(
        r"[^a-zA-Z0-9\s-]",
        "",
        text,
    )

    text = re.sub(
        r"[\s-]+",
        "-",
        text,
    )

    return text.strip("-").lower()


def make_calendar_url(title):
    slug = slugify(title)

    return "https://www.uiu.ac.bd/" "academics/calendar/" f"{slug}/"


def extract_year(title):
    match = re.search(
        r"\b(20\d{2})\b",
        title,
    )

    if match:
        return match.group(1)

    return ""


def extract_titles_from_page(soup):
    titles = []
    seen = set()

    for tag in soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "a",
            "button",
            "div",
            "span",
        ]
    ):
        text = normalize_title(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not is_calendar_title(text):
            continue

        key = text.lower()

        if key in seen:
            continue

        seen.add(key)

        titles.append(text)

    return titles


def extract_calendar_titles(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    page_text = soup.get_text(
        "\n",
        strip=True,
    )

    lines = [normalize_title(line) for line in page_text.splitlines()]

    titles = []
    seen = set()

    for line in lines:
        if not is_calendar_title(line):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)

        titles.append(line)

    if titles:
        return titles

    return extract_titles_from_page(soup)


def build_calendar_entries(titles):
    entries = []
    seen = set()

    for title in titles:
        title = normalize_title(title)

        if not is_calendar_title(title):
            continue

        key = title.lower()

        if key in seen:
            continue

        seen.add(key)

        url = make_calendar_url(title)

        entries.append(
            {
                "title": title,
                "url": url,
                "year": extract_year(title),
            }
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

        titles = extract_calendar_titles(response.text)

        entries = build_calendar_entries(titles)

        return entries


async def get_latest_calendars(
    limit=5,
):
    calendars = await fetch_calendars()

    return calendars[:limit]


async def sync_calendars():
    calendars = await fetch_calendars()

    return {
        "new": [],
        "updated": [],
        "calendars": calendars,
    }
