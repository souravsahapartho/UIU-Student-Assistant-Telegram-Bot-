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
        calendars = await get_latest_calendars(5)

        if not calendars:
            await update.message.reply_text("⚠️ No academic calendars found right now.")
            return

        text = "📅 <b>Academic Calendar</b>\n\n"

        buttons = []

        for index, calendar in enumerate(
            calendars,
            start=1,
        ):
            title = calendar["title"]
            year = calendar["year"]
            url = calendar["url"]

            text += f"<b>{index}. {title}</b>\n" f"📅 {year}\n\n"

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📄 {index}. View Calendar ↗",
                        url=url,
                    )
                ]
            )

        text += "🔗 Each button opens the " "original UIU calendar page."

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(
            "Academic calendar error:",
            e,
        )

        await update.message.reply_text(
            "⚠️ Unable to load academic calendars right now."
        )
