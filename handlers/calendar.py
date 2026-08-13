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


def shorten(
    text,
    length=700,
):

    if not text:
        return ""

    if len(text) <= length:
        return text

    shortened = text[:length]

    if " " in shortened:
        shortened = shortened.rsplit(
            " ",
            1,
        )[0]

    return shortened + "..."


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.message

    await message.reply_text(
        "📅 **Academic Calendar**\n\n" "🔄 Fetching the latest calendars from UIU...",
        parse_mode="Markdown",
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

        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        content = calendar.get(
            "content",
            "",
        )

        url = calendar.get(
            "url",
            "",
        )

        keyboard = []

        if url:

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📄 View Full Calendar",
                        url=url,
                    )
                ]
            ]

        text = f"📅 **{title}**\n\n" f"{shorten(content)}"

        await message.reply_text(
            text,
            reply_markup=(InlineKeyboardMarkup(keyboard) if keyboard else None),
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
