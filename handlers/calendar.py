from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)

from services.calendar_service import (
    fetch_calendars,
)


def shorten(text, length=700):
    if len(text) <= length:
        return text

    return (
        text[:length].rsplit(
            " ",
            1,
        )[0]
        + "..."
    )


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    await message.reply_text(
        "📅 Academic Calendar\n\n" "🔄 Fetching the latest calendar..."
    )

    try:
        calendars = await fetch_calendars()

    except Exception:
        await message.reply_text(
            "⚠️ Unable to fetch the academic calendar right now.\n\n"
            "Please try again later."
        )

        return

    if not calendars:
        await message.reply_text("⚠️ No academic calendar was found.")

        return

    calendars = calendars[:6]

    for calendar in calendars:

        keyboard = [
            [
                InlineKeyboardButton(
                    "📄 View Full Calendar",
                    url=calendar["url"],
                )
            ]
        ]

        text = "📅 " + calendar["title"] + "\n\n" + shorten(calendar["content"])

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
