import re
import httpx
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    )
}


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


def is_calendar_url(url):
    if not url:
        return False

    url = normalize_url(url)

    if "/academics/calendar/" not in url:
        return False

    if url.rstrip("/") == CALENDAR_URL.rstrip("/"):
        return False

    return True


def is_real_calendar_title(title):
    title = clean_text(title)

    if not title:
        return False

    lower = title.lower()

    if len(title) < 10:
        return False

    blocked = [
        "notice",
        "notices",
        "event",
        "events",
        "scholarship award list",
        "course enrollment",
        "orientation notice",
        "gymnasium",
        "admission test",
        "seminar",
        "workshop",
        "spotlight",
        "download pdf",
        "view more",
        "print",
    ]

    for word in blocked:
        if word in lower:
            return False

    if not re.search(
        r"\b20\d{2}\b",
        title,
    ):
        return False

    calendar_words = [
        "semester",
        "trimester",
        "b. pharm",
        "b pharm",
        "pharm.",
    ]

    return any(word in lower for word in calendar_words)


def extract_year(title):
    match = re.search(
        r"\b(20\d{2})\b",
        title,
    )

    if match:
        return match.group(1)

    return ""


def extract_title_from_link(link):
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
        alt = clean_text(
            image.get(
                "alt",
                "",
            )
        )

        if alt:
            return alt

    return ""


def find_calendar_section(soup):
    headings = soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]
    )

    for heading in headings:
        text = clean_text(
            heading.get_text(
                " ",
                strip=True,
            )
        )

        if text.lower() == "academic calendar":
            return heading

    return None


def extract_from_section(section):
    results = []
    seen_urls = set()

    if not section:
        return results

    current = section

    for _ in range(20):
        current = current.find_next_sibling()

        if not current:
            break

        text = clean_text(
            current.get_text(
                " ",
                strip=True,
            )
        )

        lower = text.lower()

        if lower.startswith("notices"):
            break

        if lower.startswith("events"):
            break

        for link in current.find_all(
            "a",
            href=True,
        ):
            url = normalize_url(
                link.get(
                    "href",
                    "",
                )
            )

            if not is_calendar_url(url):
                continue

            title = extract_title_from_link(link)

            if not is_real_calendar_title(title):
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            results.append(
                {
                    "title": title,
                    "url": url,
                    "year": extract_year(title),
                }
            )

    return results


def extract_from_all_calendar_links(soup):
    results = []
    seen_urls = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        url = normalize_url(
            link.get(
                "href",
                "",
            )
        )

        if not is_calendar_url(url):
            continue

        title = extract_title_from_link(link)

        if not is_real_calendar_title(title):
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        results.append(
            {
                "title": title,
                "url": url,
                "year": extract_year(title),
            }
        )

    return results


def extract_calendar_entries(html):
    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    section = find_calendar_section(soup)

    results = extract_from_section(section)

    if not results:
        results = extract_from_all_calendar_links(soup)

    unique = []
    seen = set()

    for item in results:
        key = item["url"].rstrip("/").lower()

        if key in seen:
            continue

        seen.add(key)

        unique.append(item)

    return unique


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


async def sync_calendars():
    current = await fetch_calendars()

    return {
        "new": [],
        "updated": [],
        "calendars": current,
    }
