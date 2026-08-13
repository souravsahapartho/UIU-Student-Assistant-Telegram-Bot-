from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from services.calendar_service import fetch_calendars


def shorten(text, length=700):
    if len(text) <= length:
        return text

    return text[:length].rsplit(" ", 1)[0] + "..."


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    message = update.message

    await message.reply_text(
        "📅 Academic Calendar\n\n" "🔄 Fetching the latest calendars..."
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
        await message.reply_text("⚠️ No academic calendar was found right now.")
        return

    calendars = calendars[:5]

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

        content = calendar.get(
            "content",
            "",
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    f"📄 {index}. {title} ↗",
                    url=url,
                )
            ]
        ]

        text = f"<b>{index}. {title}</b>\n\n" f"📅 {shorten(content)}"

        await message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
