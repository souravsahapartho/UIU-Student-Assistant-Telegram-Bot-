from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes

from services.calendar_service import (
    get_latest_calendars,
)


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    message = update.message

    if not message:
        return

    await message.reply_text("⏳ Loading academic calendars...")

    try:

        calendars = await get_latest_calendars()

        if not calendars:

            await message.reply_text(
                "📅 No academic calendar "
                "is available right now.\n\n"
                "Please try again later."
            )

            return

        text = (
            "📅 *UIU Academic Calendar*\n\n"
            "Here are the latest 5 academic "
            "calendars available from UIU:\n"
        )

        buttons = []

        for index, calendar in enumerate(
            calendars,
            start=1,
        ):

            title = calendar.get(
                "title",
                "Academic Calendar",
            )

            url = calendar.get(
                "url",
                "",
            )

            year = calendar.get(
                "year",
                "",
            )

            if year:
                display_title = f"{title}"
            else:
                display_title = title

            text += f"\n*{index}. {display_title}*"

            if year:
                text += f"\n📆 {year}"

            text += "\n"

            if url:

                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📄 {index}. View Calendar",
                            url=url,
                        )
                    ]
                )

        text += "\n🔗 Each button opens the " "original UIU calendar page/document."

        await message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=(InlineKeyboardMarkup(buttons) if buttons else None),
            disable_web_page_preview=True,
        )

    except Exception:

        await message.reply_text(
            "⚠️ Unable to load academic "
            "calendars right now.\n\n"
            "Please try again later."
        )
