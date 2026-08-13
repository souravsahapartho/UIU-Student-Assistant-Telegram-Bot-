from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import ContextTypes

from services.calendar_service import (
    get_latest_calendars,
)


async def academic_calendar(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    try:
        calendars = await get_latest_calendars(limit=5)

        if not calendars:
            await update.message.reply_text(
                "📅 No academic calendars found.\n\n" "Please try again later."
            )
            return

        lines = [
            "📅 <b>Academic Calendar</b>",
            "",
        ]

        buttons = []

        for index, calendar in enumerate(
            calendars,
            start=1,
        ):
            title = calendar.get(
                "title",
                "Academic Calendar",
            )

            year = calendar.get(
                "year",
                "",
            )

            url = calendar.get(
                "url",
                "",
            )

            lines.append(f"<b>{index}. {title}</b>")

            if year:
                lines.append(f"📅 {year}")

            lines.append("")

            if url:
                buttons.append(
                    [
                        InlineKeyboardButton(
                            f"📄 {index}. View Calendar",
                            url=url,
                        )
                    ]
                )

        lines.append("🔗 Each button opens the original UIU academic calendar page.")

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ Unable to load academic calendars right now.\n\n"
            "Please try again later."
        )
