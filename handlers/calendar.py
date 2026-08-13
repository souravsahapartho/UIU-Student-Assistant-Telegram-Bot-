import re

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from services.calendar_service import (
    fetch_calendars,
)


def get_year(calendar):
    year = calendar.get(
        "year",
        "",
    )

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

    if match:
        return match.group(0)

    return ""


def get_button_title(title):
    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip()

    clean = re.sub(
        r"\s*\[Revised\]\s*$",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    year_match = re.search(
        r"\b20\d{2}\b",
        clean,
    )

    year = year_match.group(0) if year_match else ""

    lower = clean.lower()

    if "pharmacy" in lower:
        if "fall" in lower:
            return f"Pharmacy — Fall {year} Semester"

        if "spring" in lower:
            return f"Pharmacy — Spring {year} Semester"

        if "summer" in lower:
            return f"Pharmacy — Summer {year} Semester"

        return f"Pharmacy — {year}"

    if "undergraduate" in lower:
        if "summer" in lower:
            return f"Undergraduate — " f"Summer {year} Trimester"

        if "spring" in lower:
            return f"Undergraduate — " f"Spring {year} Trimester"

        if "fall" in lower:
            return f"Undergraduate — " f"Fall {year} Trimester"

        return f"Undergraduate — {year}"

    if "graduate" in lower:
        if "summer" in lower:
            return f"Graduate — " f"Summer {year} Trimester"

        if "spring" in lower:
            return f"Graduate — " f"Spring {year} Trimester"

        if "fall" in lower:
            return f"Graduate — " f"Fall {year} Trimester"

        return f"Graduate — {year}"

    return clean


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

    await message.reply_text(
        "📅 <b>Academic Calendar</b>\n\n"
        "📌 Tap a calendar button to view "
        "the official UIU page.",
        parse_mode="HTML",
    )

    for index, calendar in enumerate(
        calendars,
        1,
    ):
        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        year = get_year(calendar)

        url = calendar.get(
            "url",
            "",
        )

        button_title = get_button_title(title)

        text = f"<b>{index}. {title}</b>\n" f"📅 {year}"

        keyboard = []

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
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
