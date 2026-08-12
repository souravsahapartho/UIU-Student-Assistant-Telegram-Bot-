import logging
import feedparser
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from keyboards import get_main_menu, get_links_keyboard
from database import (
    log_user_activity,
    get_recent_notices,
    get_notification_status,
    toggle_notification,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_user_activity(user.id, user.first_name, user.username)

    welcome_msg = (
        f"👋 Welcome to **UIU Smart Assistant**, {user.first_name}!\n\n"
        "Your personal assistant for:\n"
        "🎓 CGPA calculation\n"
        "💰 Tuition fee calculation\n"
        "📚 Academic resources\n"
        "🔗 Important UIU links\n"
        "📢 Real-time Notices and calendar\n\n"
        "👨‍💻 _Made with ❤️ by @souravsahapartho_\n\n"
        "👇 Select an option from the menu below to get started."
    )
    await update.message.reply_text(
        welcome_msg, reply_markup=get_main_menu(), parse_mode="Markdown"
    )


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ **Help Center**\n\n"
        "🎓 **CGPA Calculator:** Accurately calculate semester & overall CGPA.\n"
        "💰 **Fee Calculator:** Estimate tuition fees including waivers & retakes.\n"
        "📢 **Notices:** Automatically get UIU latest notices.\n"
        "⚙️ **Settings:** Turn On/Off automatic notice alerts.\n\n"
        "If you face issues, type /start to refresh the bot."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 **UIU Smart Assistant**\n\n"
        "A student-focused Telegram assistant for United International University.\n"
        "Version 2.0.0\n\n"
        "👨‍💻 **Developer:** @souravsahapartho\n\n"
        "*Disclaimer:* Fee and academic policy information may change. "
        "Please verify important decisions with official UIU sources."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def important_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔗 **Important UIU Links**\nSelect a link below to open it in your browser:"
    await update.message.reply_text(
        text, reply_markup=get_links_keyboard(), parse_mode="Markdown"
    )


async def academic_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 **Academic Information**\n\nFor official academic rules, grading policies, and retake guidelines, please visit the official UIU website or check your UCAM account."
    await update.message.reply_text(text, parse_mode="Markdown")


async def academic_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📅 **Academic Calendar**\n\nYou can find the updated academic calendar on the official UIU website: [UIU Academic Calendar](https://www.uiu.ac.bd/academics/calendar/)"
    await update.message.reply_text(
        text, parse_mode="Markdown", disable_web_page_preview=True
    )


async def notices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Fetching latest notices from UIU website...")

    feed_url = "https://www.uiu.ac.bd/notice/feed/"
    try:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            msg = "📢 **Latest UIU Notices:**\n\n"
            for i, entry in enumerate(feed.entries[:5]):
                msg += f"📌 **{entry.title}**\n🔗 [Read Full Notice]({entry.link})\n\n"
            await update.message.reply_text(
                msg, parse_mode="Markdown", disable_web_page_preview=True
            )
            return
    except Exception as e:
        logger.error(f"Error fetching live notices: {e}")

    db_notices = get_recent_notices(5)
    if db_notices:
        msg = "📢 **Recent UIU Notices:**\n\n"
        for notice in db_notices:
            msg += (
                f"📌 **{notice['title']}**\n🔗 [Read Full Notice]({notice['link']})\n\n"
            )
        await update.message.reply_text(
            msg, parse_mode="Markdown", disable_web_page_preview=True
        )
    else:
        await update.message.reply_text(
            "📢 No notices available right now. Please check back later."
        )


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_on = get_notification_status(user_id)

    status_text = "🟢 ON" if is_on else "🔴 OFF"
    keyboard = [
        [
            InlineKeyboardButton(
                f"🔔 Notice Alerts: {status_text}", callback_data="toggle_alerts"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚙️ **Settings Menu**\n\n"
        "Manage your bot preferences here. You can turn off automatic notice alerts if you don't want to be disturbed.",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "toggle_alerts":
        user_id = query.from_user.id
        new_status = toggle_notification(user_id)

        status_text = "🟢 ON" if new_status else "🔴 OFF"
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🔔 Notice Alerts: {status_text}", callback_data="toggle_alerts"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        state_msg = "enabled" if new_status else "disabled"
        await query.edit_message_text(
            f"⚙️ **Settings Menu**\n\n✅ Notice alerts have been **{state_msg}**.",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Action cancelled. Returning to main menu.", reply_markup=get_main_menu()
    )


async def show_not_implemented(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This feature is coming soon! Stay tuned.", reply_markup=get_main_menu()
    )
