from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from services.calendar_service import fetch_calendars


def get_year(calendar):
    title = calendar.get("title", "")
    year = calendar.get("year", "")

    if year:
        return year

    import re

    match = re.search(
        r"\b20\d{2}\b",
        title,
    )

    return match.group(0) if match else ""


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

    text_parts = ["📅 <b>Academic Calendar</b>"]

    buttons = []

    for index, calendar in enumerate(
        calendars,
        1,
    ):
        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        year = get_year(calendar)

        text_parts.append(f"\n<b>{index}. {title}</b>\n" f"📅 {year}")

        url = calendar.get(
            "url",
            "",
        )

        if url:
            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📄 {index}. View Calendar ↗",
                        url=url,
                    )
                ]
            )

    text_parts.append("\n🔗 Each button opens the original UIU academic calendar.")

    await message.reply_text(
        "\n".join(text_parts),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
