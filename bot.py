import logging
import asyncio
import sys
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

from config import Config
from database import init_db
from states import *

# Handlers imports
from handlers.general import (
    start,
    show_links,
    show_about,
    show_help,
    handle_cancel,
    show_not_implemented,
)
from handlers.cgpa import (
    cgpa_start,
    cgpa_new_calc,
    get_prev_credits,
    get_prev_cgpa,
    get_course_count,
    get_course_credit,
    get_course_grade,
    cgpa_cancel,
)
from handlers.fee import (
    fee_start,
    get_reg_credits,
    get_retake_count,
    get_retake_credits,
    get_discount_type,
    get_discount_percent,
    fee_cancel,
)
from handlers.admin import admin_panel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "⚠ Something went wrong. Please try again or type /start to restart."
        )


def main():
    # --- Fix for Windows and newer Python versions ---
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    # -------------------------------------------------

    # Setup
    Config.validate()
    init_db()

    app = Application.builder().token(Config.BOT_TOKEN).build()

    # --- Conversation Handlers ---

    # 1. CGPA Calculator Conversation
    cgpa_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🎓 CGPA Calculator$"), cgpa_start)
        ],
        states={
            CGPA_MENU_CHOICE: [
                MessageHandler(filters.Regex("^➕ New Calculation$"), cgpa_new_calc)
            ],
            CGPA_PREV_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_prev_credits
                )
            ],
            CGPA_PREV_CGPA: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_prev_cgpa
                )
            ],
            CGPA_COURSE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_count
                )
            ],
            CGPA_COURSE_CREDIT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_credit
                )
            ],
            CGPA_COURSE_GRADE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_grade
                )
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌ Cancel$"), cgpa_cancel),
            CommandHandler("cancel", cgpa_cancel),
        ],
        per_user=True,
    )

    # 2. Fee Calculator Conversation
    fee_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Fee Calculator$"), fee_start)],
        states={
            FEE_REG_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_reg_credits
                )
            ],
            FEE_RETAKE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_retake_count
                )
            ],
            FEE_RETAKE_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_retake_credits
                )
            ],
            FEE_DISCOUNT_TYPE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_discount_type
                )
            ],
            FEE_DISCOUNT_PERCENT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_discount_percent
                )
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌ Cancel$"), fee_cancel),
            CommandHandler("cancel", fee_cancel),
        ],
        per_user=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", show_help))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(cgpa_conv_handler)
    app.add_handler(fee_conv_handler)

    # Menu Button Handlers
    app.add_handler(MessageHandler(filters.Regex("^🔗 Important Links$"), show_links))
    app.add_handler(MessageHandler(filters.Regex("^👤 About$"), show_about))
    app.add_handler(MessageHandler(filters.Regex("^❓ Help$"), show_help))
    app.add_handler(MessageHandler(filters.Regex("^(❌ Cancel)$"), handle_cancel))

    # Unimplemented Placeholders (To satisfy structural requirement smoothly)
    app.add_handler(
        MessageHandler(
            filters.Regex(
                "^(🎁 Scholarship Calculator|📚 Academic Info|📅 Academic Calendar|📢 Notices|⚙️ Settings)$"
            ),
            show_not_implemented,
        )
    )

    # Error Handler
    app.add_error_handler(error_handler)

    print("UIU Smart Assistant is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
