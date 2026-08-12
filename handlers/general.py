from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_main_menu, get_links_keyboard
from database import log_user_activity


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    log_user_activity(user.id, user.first_name, user.username)

    welcome_msg = (
        f"👋 Hello {user.first_name}! Welcome to **UIU Smart Assistant** 🎓\n\n"
        "I am your all-in-one digital companion for United International University. "
        "From calculating your CGPA to estimating trimester fees, I've got you covered!\n\n"
        "✨ **What I can do for you:**\n"
        "📊 **Calculate CGPA:** Accurate semester & overall tracking.\n"
        "💰 **Estimate Fees:** Tuition, retakes, and waivers combined.\n"
        "📚 **Academic Info:** Quick access to rules and resources.\n"
        "🔗 **Quick Links:** UCAM, eLMS, and more at your fingertips.\n\n"
        "👨‍💻 *Made with ❤️ by @souravsahapartho*\n\n"
        "👇 Select an option from the menu below to get started!"
    )
    await update.message.reply_text(
        welcome_msg, reply_markup=get_main_menu(), parse_mode="Markdown"
    )


async def show_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔗 **Important UIU Links**\nSelect a link below to open it in your browser:"
    await update.message.reply_text(
        text, reply_markup=get_links_keyboard(), parse_mode="Markdown"
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 **UIU Smart Assistant**\n\n"
        "A student-focused Telegram assistant for United International University.\n"
        "Version 1.0.0\n\n"
        "*Disclaimer:* Fee and academic policy information may change. "
        "Please verify important decisions with official UIU sources."
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❓ **Help Center**\n\n"
        "🎓 **CGPA Calculator:** Follow the steps to enter your previous credits and CGPA, then enter your current semester details.\n"
        "💰 **Fee Calculator:** Provides an estimate based on current UIU tuition rules, including retake rules and scholarships.\n"
        "❌ **Cancel:** You can press 'Cancel' at any time to stop a process and return to the main menu.\n\n"
        "If you face issues, type /start to refresh the bot."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback cancel handler if they type Cancel outside a conversation"""
    await update.message.reply_text(
        "Action cancelled. Returning to main menu.", reply_markup=get_main_menu()
    )


async def show_not_implemented(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This feature is coming soon! Stay tuned.", reply_markup=get_main_menu()
    )
