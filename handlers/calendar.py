import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from services.calendar_service import fetch_calendars


def get_year(calendar):
    year = calendar.get("year", "")

    if year:
        return year

    title = calendar.get(
        "title",
        "",
    )

    match = re.search(
        r"\b20\d{2}\b",
        title,
    )

    return match.group(0) if match else ""


def get_button_title(title):
    clean_title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip()

    clean_title = re.sub(
        r"\s*\[Revised\]\s*$",
        "",
        clean_title,
        flags=re.IGNORECASE,
    ).strip()

    year_match = re.search(
        r"\b20\d{2}\b",
        clean_title,
    )

    year = year_match.group(0) if year_match else ""

    if "pharmacy" in clean_title.lower():
        if "fall" in clean_title.lower():
            return f"Pharmacy — Fall {year} Semester"

        if "spring" in clean_title.lower():
            return f"Pharmacy — Spring {year} Semester"

        if "summer" in clean_title.lower():
            return f"Pharmacy — Summer {year} Semester"

        return f"Pharmacy — {year}"

    if "undergraduate" in clean_title.lower():
        if "summer" in clean_title.lower():
            return f"Undergraduate — Summer {year} Trimester"

        if "spring" in clean_title.lower():
            return f"Undergraduate — Spring {year} Trimester"

        if "fall" in clean_title.lower():
            return f"Undergraduate — Fall {year} Trimester"

        return f"Undergraduate — {year}"

    if "graduate" in clean_title.lower():
        if "summer" in clean_title.lower():
            return f"Graduate — Summer {year} Trimester"

        if "spring" in clean_title.lower():
            return f"Graduate — Spring {year} Trimester"

        if "fall" in clean_title.lower():
            return f"Graduate — Fall {year} Trimester"

        return f"Graduate — {year}"

    return clean_title


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.effective_message

    try:
        calendars = await fetch_calendars()

    except Exception:
        await message.reply_text(
            "⚠️ Unable to fetch the academic calendar right now.\n\n"
            "Please try again later."
        )
        return

    if not calendars:
        await message.reply_text("⚠️ No academic calendar was found right now.")
        return

    calendars = calendars[:5]

    text_parts = [
        "📅 <b>Academic Calendar</b>",
        "",
        "📌 Tap the button below each calendar to view the official UIU page.",
    ]

    keyboard = []

    for index, calendar in enumerate(
        calendars,
        1,
    ):
        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        url = calendar.get(
            "url",
            "",
        )

        year = get_year(calendar)

        button_title = get_button_title(title)

        text_parts.extend(
            [
                "",
                f"<b>{index}. {title}</b>",
                f"📅 {year}",
            ]
        )

        if url:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📄 {button_title} ↗",
                        url=url,
                    )
                ]
            )

    await message.reply_text(
        "\n".join(text_parts),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
