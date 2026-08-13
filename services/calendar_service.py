import re
import hashlib
from typing import List, Dict, Any

import httpx
from bs4 import BeautifulSoup

from database import (
    get_setting,
    update_setting,
)

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

MAX_CALENDARS = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.uiu.ac.bd/",
}


async def fetch_calendar_page() -> str:
    timeout = httpx.Timeout(
        20.0,
        connect=10.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=HEADERS,
        follow_redirects=True,
    ) as client:

        response = await client.get(CALENDAR_URL)

        response.raise_for_status()

        return response.text


def clean_text(value: str) -> str:
    if not value:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def normalize_url(url: str) -> str:

    if not url:
        return ""

    url = url.strip()

    if url.startswith("//"):
        return "https:" + url

    if url.startswith("/"):
        return "https://www.uiu.ac.bd" + url

    if url.startswith("http://"):
        return "https://" + url[7:]

    if not url.startswith("http"):
        return "https://www.uiu.ac.bd/" + url.lstrip("/")

    return url


def is_calendar_link(
    text: str,
    url: str,
) -> bool:

    combined = (f"{text} {url}").lower()

    keywords = [
        "academic calendar",
        "calendar",
        "semester",
        "trimester",
        "spring",
        "summer",
        "fall",
        "autumn",
    ]

    file_keywords = [
        ".pdf",
        ".doc",
        ".docx",
    ]

    return any(keyword in combined for keyword in keywords) or any(
        keyword in combined for keyword in file_keywords
    )


def extract_year_or_term(
    text: str,
    url: str,
) -> str:

    combined = f"{text} {url}"

    year_matches = re.findall(
        r"\b20\d{2}\b",
        combined,
    )

    years = []

    for year in year_matches:
        if year not in years:
            years.append(year)

    if years:
        return years[0]

    return ""


def create_calendar_id(
    title: str,
    url: str,
) -> str:

    raw = f"{title.strip().lower()}|" f"{url.strip().lower()}"

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def parse_calendar_items(
    html: str,
) -> List[Dict[str, Any]]:

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    results = []
    seen_urls = set()

    for anchor in soup.find_all("a"):

        href = anchor.get("href")

        if not href:
            continue

        url = normalize_url(href)

        text = clean_text(
            anchor.get_text(
                " ",
                strip=True,
            )
        )

        title = text

        parent = anchor.parent

        if not title and parent is not None:
            title = clean_text(
                parent.get_text(
                    " ",
                    strip=True,
                )
            )

        if not is_calendar_link(
            title,
            url,
        ):
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        year = extract_year_or_term(
            title,
            url,
        )

        if not title:
            title = f"Academic Calendar {year}" if year else "Academic Calendar"

        title = clean_text(title)

        calendar_id = create_calendar_id(
            title,
            url,
        )

        results.append(
            {
                "id": calendar_id,
                "title": title,
                "url": url,
                "year": year,
            }
        )

    return results


def score_calendar(
    item: Dict[str, Any],
) -> int:

    title = item.get(
        "title",
        "",
    ).lower()

    url = item.get(
        "url",
        "",
    ).lower()

    score = 0

    years = re.findall(
        r"\b20\d{2}\b",
        f"{title} {url}",
    )

    if years:

        try:
            score += int(max(years)) * 100
        except ValueError:
            pass

    terms = [
        "spring",
        "summer",
        "fall",
        "autumn",
        "trimester",
        "semester",
    ]

    for index, term in enumerate(terms):
        if term in title:
            score += len(terms) - index

    if ".pdf" in url:
        score += 2

    return score


def get_latest_five(
    items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    unique = {}

    for item in items:

        item_id = item.get("id")

        if item_id:
            unique[item_id] = item

    items = list(unique.values())

    items.sort(
        key=score_calendar,
        reverse=True,
    )

    return items[:MAX_CALENDARS]


def get_saved_calendars() -> List[Dict[str, Any]]:

    raw = get_setting(
        "ACADEMIC_CALENDARS",
        "[]",
    )

    if isinstance(
        raw,
        list,
    ):
        return raw

    try:

        import json

        data = json.loads(str(raw))

        if isinstance(
            data,
            list,
        ):
            return data

    except Exception:
        pass

    return []


def save_calendars(
    calendars: List[Dict[str, Any]],
):

    import json

    update_setting(
        "ACADEMIC_CALENDARS",
        json.dumps(
            calendars,
            ensure_ascii=False,
        ),
    )


def find_new_calendars(
    old: List[Dict[str, Any]],
    new: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    old_ids = {item.get("id") for item in old}

    return [item for item in new if item.get("id") not in old_ids]


def find_updated_calendars(
    old: List[Dict[str, Any]],
    new: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    old_map = {item.get("id"): item for item in old if item.get("id")}

    updated = []

    for item in new:

        item_id = item.get("id")

        if not item_id:
            continue

        old_item = old_map.get(item_id)

        if not old_item:
            continue

        if old_item.get("title") != item.get("title") or old_item.get(
            "url"
        ) != item.get("url"):
            updated.append(item)

    return updated


async def sync_calendars():

    html = await fetch_calendar_page()

    fetched = parse_calendar_items(html)

    latest = get_latest_five(fetched)

    old = get_saved_calendars()

    new_items = find_new_calendars(
        old,
        latest,
    )

    updated_items = find_updated_calendars(
        old,
        latest,
    )

    save_calendars(latest)

    return {
        "calendars": latest,
        "new": new_items,
        "updated": updated_items,
    }


async def get_latest_calendars():

    try:

        calendars = get_saved_calendars()

        if calendars:
            return get_latest_five(calendars)

        result = await sync_calendars()

        return result.get(
            "calendars",
            [],
        )

    except Exception:

        return get_saved_calendars()
