import httpx
from bs4 import BeautifulSoup

CALENDAR_URL = "https://www.uiu.ac.bd/academics/calendar/"

FALL_2026_PHARMACY = "https://www.uiu.ac.bd/academics/calendar/fall-2026-semester-bachelor-of-pharmacy-b-pharm/"

CALENDAR_FALLBACKS = [
    {
        "title": "Fall 2026 Semester Bachelor of Pharmacy (B. Pharm.)",
        "year": "2026",
        "url": FALL_2026_PHARMACY,
    },
    {
        "title": "Summer 2026 Trimester Undergraduate Programs",
        "year": "2026",
        "url": "https://www.uiu.ac.bd/academics/calendar/summer-2026-trimester-undergraduate-programs/",
    },
    {
        "title": "Summer 2026 Trimester Graduate Programs",
        "year": "2026",
        "url": "https://www.uiu.ac.bd/academics/calendar/summer-2026-trimester-graduate-programs/",
    },
    {
        "title": "Spring 2026 Trimester Undergraduate Programs [Revised]",
        "year": "2026",
        "url": "https://www.uiu.ac.bd/academics/calendar/spring-2026-trimester-undergraduate-programs/",
    },
    {
        "title": "Spring 2026 Trimester Graduate Programs [Revised]",
        "year": "2026",
        "url": "https://www.uiu.ac.bd/academics/calendar/spring-2026-trimester-graduate-programs/",
    },
]


async def fetch_calendars():
    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 " "AppleWebKit/537.36 " "Chrome/151.0 Safari/537.36"
                )
            },
        ) as client:
            response = await client.get(CALENDAR_URL)

            if response.status_code == 200:
                soup = BeautifulSoup(
                    response.text,
                    "html.parser",
                )

                found = []

                for item in CALENDAR_FALLBACKS:
                    link = soup.find(
                        "a",
                        href=lambda href: (
                            href and item["url"].rstrip("/") in href.rstrip("/")
                        ),
                    )

                    if link:
                        found.append(item)

                if len(found) >= 5:
                    return found[:5]

    except Exception as e:
        print(
            "Calendar fetch error:",
            e,
        )

    return CALENDAR_FALLBACKS[:5]


async def get_latest_calendars(limit=5):
    calendars = await fetch_calendars()

    return calendars[:limit]


async def sync_calendars():
    calendars = await fetch_calendars()

    return {
        "new": [],
        "updated": [],
        "calendars": calendars,
    }
