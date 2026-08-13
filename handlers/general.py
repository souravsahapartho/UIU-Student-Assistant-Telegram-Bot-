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


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.message.from_user

    log_user_activity(
        user.id,
        user.first_name,
        user.username,
    )

    welcome_msg = (
        f"👋 Welcome to **UIU Smart Assistant**, "
        f"{user.first_name}!\n\n"
        "Your personal assistant for:\n"
        "🎓 CGPA calculation\n"
        "💰 Tuition fee calculation\n"
        "📚 Academic resources\n"
        "🔗 Important UIU links\n"
        "📢 Real-time Notices and calendar\n\n"
        "👨‍💻 _Made with ❤️ by @souravsahapartho_\n\n"
        "👇 Select an option from the menu below "
        "to get started."
    )

    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )


async def show_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    help_text = (
        "❓ **Help Center**\n\n"
        "🎓 **CGPA Calculator:** "
        "Accurately calculate semester & overall CGPA.\n\n"
        "💰 **Fee Calculator:** "
        "Estimate tuition fees including waivers & retakes.\n\n"
        "🎁 **Scholarship Calculator:** "
        "Check scholarship-related calculations.\n\n"
        "📚 **Academic Information:** "
        "Access important academic information.\n\n"
        "📢 **Notices:** "
        "Get the latest UIU notices.\n\n"
        "⚙️ **Settings:** "
        "Manage notification preferences.\n\n"
        "If you face issues, use /start to restart the bot."
    )

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
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
        "*Disclaimer:* Fee and academic policy "
        "information may change. Please verify "
        "important decisions with official UIU sources."
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
            ),
        ],
    ]

    await update.message.reply_text(
        "📚 **Academic Information**\n\n" "Select a topic:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


def grading_system_text():
    return (
        "📚 <b>UIU Grading System</b>\n\n"
        "<pre>"
        "Letter   Grade   Marks     Assessment\n"
        "────────────────────────────────────\n"
        "A        4.00    90–100    Outstanding\n"
        "A-       3.67    86–89     Excellent\n"
        "B+       3.33    82–85     Very Good\n"
        "B        3.00    78–81     Good\n"
        "B-       2.67    74–77     Above Average\n"
        "C+       2.33    70–73     Average\n"
        "C        2.00    66–69     Below Average\n"
        "C-       1.67    62–65     Poor\n"
        "D+       1.33    58–61     Very Poor\n"
        "D        1.00    55–57     Pass\n"
        "F        0.00    0–54      Fail\n"
        "</pre>\n\n"
        "📌 This grading scale is used for "
        "CGPA calculation."
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
                ),
            ],
        ]

        await query.edit_message_text(
            "📚 **Academic Information**\n\n" "Select a topic:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return

    if query.data == "acad_grading":
        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Academic Information",
                    callback_data="acad_back_info",
                )
            ]
        ]

        await query.edit_message_text(
            grading_system_text(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )
        return

    information = {
        "acad_admission": (
            "🎓 **Admission**\n\n"
            "For current admission requirements "
            "and procedures, please check the "
            "official UIU website."
        ),
        "acad_registration": (
            "📝 **Registration**\n\n"
            "Course registration information and "
            "deadlines should be verified through "
            "UCAM and official UIU announcements."
        ),
        "acad_credit": (
            "📊 **Credit System**\n\n"
            "Credit requirements depend on the "
            "academic program. Check your "
            "department's official curriculum."
        ),
        "acad_retake": (
            "🔄 **Retake Rules**\n\n"
            "Retake and improvement policies may "
            "change. Please verify the current "
            "policy through official UIU sources."
        ),
        "acad_graduation": (
            "🎯 **Graduation Requirements**\n\n"
            "Graduation requirements depend on "
            "your program and academic regulations."
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

    except Exception as e:
        logger.error(
            "Error fetching live notices: %s",
            e,
        )

    db_notices = get_recent_notices(5)

    if db_notices:
        msg = "📢 **Recent UIU Notices:**\n\n"

        for notice in db_notices:
            msg += (
                f"📌 **{notice['title']}**\n"
                f"🔗 [Read Full Notice]"
                f"({notice['link']})\n\n"
            )

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

    status = get_notification_status(user_id)

    status_text = "🟢 ON" if status else "🔴 OFF"

    keyboard = [
        [
            InlineKeyboardButton(
                f"🔔 Notifications: {status_text}",
                callback_data="toggle_alerts",
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Main Menu",
                callback_data="settings_back",
            )
        ],
    ]

    await update.message.reply_text(
        "⚙️ **Settings**\n\n" "Manage your notification preferences.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "toggle_alerts":
        user_id = query.from_user.id

        new_status = toggle_notification(user_id)

        status_text = "🟢 ON" if new_status else "🔴 OFF"

        keyboard = [
            [
                InlineKeyboardButton(
                    f"🔔 Notifications: {status_text}",
                    callback_data="toggle_alerts",
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Main Menu",
                    callback_data="settings_back",
                )
            ],
        ]

        await query.edit_message_text(
            "⚙️ **Settings**\n\n" f"🔔 Notifications are now " f"{status_text}.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "settings_back":
        await query.edit_message_text("Use /start to return to the main menu.")


async def handle_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "❌ Cancelled.\n\n" "Use /start to return to the main menu.",
        reply_markup=get_main_menu(),
    )


async def show_not_implemented(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text("🚧 This feature is currently being updated.")
