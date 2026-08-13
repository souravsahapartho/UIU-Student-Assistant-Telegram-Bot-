import asyncio
import logging
import feedparser

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import ContextTypes

from keyboards import (
    get_main_menu,
    get_links_keyboard,
)

from database import (
    log_user_activity,
    get_recent_notices,
    get_notification_status,
    toggle_notification,
)

logger = logging.getLogger(__name__)


async def save_user_activity(
    user,
):
    try:
        await asyncio.to_thread(
            log_user_activity,
            user.id,
            user.first_name or "",
            user.username,
        )
    except Exception as error:
        logger.warning(
            "User activity logging failed: %s",
            error,
        )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return

    user = update.effective_user

    welcome_msg = (
        f"👋 Welcome to **UIU Smart Assistant**, "
        f"{user.first_name if user else 'Student'}!\n\n"
        "Your personal assistant for:\n"
        "🎓 CGPA calculation\n"
        "💰 Tuition fee calculation\n"
        "🎁 Scholarship calculation\n"
        "📚 Academic resources\n"
        "🔗 Important UIU links\n"
        "📅 Academic calendar\n"
        "📢 Latest notices\n\n"
        "👨‍💻 _Made with ❤️ by @souravsahapartho_\n\n"
        "👇 Select an option from the menu below."
    )

    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )

    if user:
        asyncio.create_task(save_user_activity(user))


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    help_text = (
        "❓ **Help Center**\n\n"
        "🎓 **CGPA Calculator**\n"
        "Calculate semester GPA and updated overall CGPA.\n\n"
        "💰 **Fee Calculator**\n"
        "Estimate tuition fees, retake fees, "
        "scholarships, waivers and installments.\n\n"
        "🎁 **Scholarship Calculator**\n"
        "Check scholarship-related calculations.\n\n"
        "📚 **Academic Information**\n"
        "Access important academic information.\n\n"
        "📢 **Notices**\n"
        "Get the latest UIU notices.\n\n"
        "📅 **Academic Calendar**\n"
        "Fetch the latest academic calendars directly from UIU.\n\n"
        "🔗 **Important Links**\n"
        "Quick access to official UIU resources.\n\n"
        "If you face any issue, use /start to restart the bot."
    )

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )


async def show_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await help_command(
        update,
        context,
    )


async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    about_text = (
        "🤖 **UIU Smart Assistant**\n\n"
        "A student-focused Telegram assistant for "
        "United International University.\n\n"
        "Version 2.0.0\n\n"
        "👨‍💻 **Developer:** @souravsahapartho\n\n"
        "*Disclaimer:* Fee and academic policy information "
        "may change. Please verify important decisions with "
        "official UIU sources."
    )

    await update.message.reply_text(
        about_text,
        parse_mode="Markdown",
    )


async def show_about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await about(
        update,
        context,
    )


async def important_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = "🔗 **Important UIU Links**\n\n" "Select a link below to open it."

    await update.message.reply_text(
        text,
        reply_markup=get_links_keyboard(),
        parse_mode="Markdown",
    )


async def show_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await important_links(
        update,
        context,
    )


async def academic_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    keyboard = [
        [
            InlineKeyboardButton(
                "🎓 Admission",
                callback_data="acad_admission",
            ),
            InlineKeyboardButton(
                "📝 Registration",
                callback_data="acad_registration",
            ),
        ],
        [
            InlineKeyboardButton(
                "📊 Credit System",
                callback_data="acad_credit",
            ),
            InlineKeyboardButton(
                "🔄 Retake Rules",
                callback_data="acad_retake",
            ),
        ],
        [
            InlineKeyboardButton(
                "🎯 Graduation",
                callback_data="acad_graduation",
            ),
            InlineKeyboardButton(
                "📚 Grading System",
                callback_data="acad_grading",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Main Menu",
                callback_data="acad_back",
            )
        ],
    ]

    await update.message.reply_text(
        "📚 **Academic Information**\n\n" "Select a topic:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def academic_info_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    if query.data == "acad_back":

        await query.edit_message_text("Use /start to return to the main menu.")

        return

    if query.data == "acad_back_info":

        await query.edit_message_text(
            "📚 **Academic Information**\n\n"
            "Please select a topic from the "
            "Academic Information menu.",
            parse_mode="Markdown",
        )

        return

    information = {
        "acad_admission": (
            "🎓 **Admission**\n\n"
            "For current admission requirements and "
            "procedures, please check the official UIU website."
        ),
        "acad_registration": (
            "📝 **Registration**\n\n"
            "Course registration information and deadlines "
            "should be verified through UCAM and official "
            "UIU announcements."
        ),
        "acad_credit": (
            "📊 **Credit System**\n\n"
            "Credit requirements depend on the academic "
            "program. Check your department's official curriculum."
        ),
        "acad_retake": (
            "🔄 **Retake Rules**\n\n"
            "Retake and improvement policies may change. "
            "Please verify the current policy through official UIU sources."
        ),
        "acad_graduation": (
            "🎯 **Graduation Requirements**\n\n"
            "Graduation requirements depend on your program "
            "and academic regulations."
        ),
        "acad_grading": (
            "📚 **Grading System**\n\n"
            "The CGPA calculator uses the configured "
            "UIU-compatible grade-point scale."
        ),
    }

    text = information.get(
        query.data,
        "Information not available.",
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ Academic Information",
                callback_data="acad_back_info",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def notices(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text("⏳ Fetching latest notices from UIU website...")

    feed_url = "https://www.uiu.ac.bd/notice/feed/"

    try:

        feed = feedparser.parse(feed_url)

        if feed.entries:

            msg = "📢 **Latest UIU Notices:**\n\n"

            for entry in feed.entries[:5]:

                title = entry.get(
                    "title",
                    "Untitled Notice",
                )

                link = entry.get(
                    "link",
                    "",
                )

                msg += f"📌 **{title}**\n" f"🔗 [Read Full Notice]({link})\n\n"

            await update.message.reply_text(
                msg,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

            return

    except Exception as error:

        logger.error(
            "Error fetching live notices: %s",
            error,
        )

    db_notices = get_recent_notices(5)

    if db_notices:

        msg = "📢 **Recent UIU Notices:**\n\n"

        for notice in db_notices:

            title = notice["title"]

            link = notice["url"] or ""

            msg += f"📌 **{title}**\n" f"🔗 [Read Full Notice]({link})\n\n"

        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

    else:

        await update.message.reply_text(
            "📢 No notices available right now. " "Please check back later."
        )


async def settings_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user_id = update.effective_user.id

    is_on = get_notification_status(user_id)

    status_text = "🟢 ON" if is_on else "🔴 OFF"

    keyboard = [
        [
            InlineKeyboardButton(
                f"🔔 Notice Alerts: {status_text}",
                callback_data="toggle_alerts",
            )
        ]
    ]

    await update.message.reply_text(
        "⚙️ **Settings Menu**\n\n" "Manage your bot notification preferences.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    if query.data != "toggle_alerts":
        return

    user_id = query.from_user.id

    new_status = toggle_notification(user_id)

    status_text = "🟢 ON" if new_status else "🔴 OFF"

    state_msg = "enabled" if new_status else "disabled"

    keyboard = [
        [
            InlineKeyboardButton(
                f"🔔 Notice Alerts: {status_text}",
                callback_data="toggle_alerts",
            )
        ]
    ]

    await query.edit_message_text(
        "⚙️ **Settings Menu**\n\n" f"✅ Notice alerts have been **{state_msg}**.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def handle_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "❌ Action cancelled.\n\n" "Returning to the main menu.",
        reply_markup=get_main_menu(),
    )


async def show_not_implemented(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "🚧 This feature is coming soon!",
        reply_markup=get_main_menu(),
    )
