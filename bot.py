import os
import asyncio
import sys
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from config import Config
from handlers.general import (
    start,
    help_command,
    about,
    academic_info,
    important_links,
    notices,
    academic_calendar,
    academic_info_callback,
    check_uiu_notices,
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
from states import (
    CGPA_MENU_CHOICE,
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
    FEE_REG_CREDITS,
    FEE_RETAKE_COUNT,
    FEE_RETAKE_CREDITS,
    FEE_DISCOUNT_TYPE,
    FEE_DISCOUNT_PERCENT,
)
from database import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    load_dotenv()
    init_db()

    app = Application.builder().token(Config.BOT_TOKEN).build()

    if app.job_queue:
        app.job_queue.run_repeating(check_uiu_notices, interval=1800, first=10)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("admin", admin_panel))

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
    app.add_handler(cgpa_conv_handler)

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
    app.add_handler(fee_conv_handler)

    app.add_handler(
        MessageHandler(filters.Regex("^📚 Academic Information$"), academic_info)
    )
    app.add_handler(
        MessageHandler(filters.Regex("^🔗 Important Links$"), important_links)
    )
    app.add_handler(MessageHandler(filters.Regex("^📢 Notices$"), notices))
    app.add_handler(
        MessageHandler(filters.Regex("^📅 Academic Calendar$"), academic_calendar)
    )
    app.add_handler(MessageHandler(filters.Regex("^❓ Help$"), help_command))
    app.add_handler(MessageHandler(filters.Regex("^👤 About$"), about))

    app.add_handler(CallbackQueryHandler(academic_info_callback, pattern="^acad_"))

    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL")

    if webhook_url:
        logger.info(f"Starting Webhook on port {port}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=Config.BOT_TOKEN,
            webhook_url=f"{webhook_url}/{Config.BOT_TOKEN}",
        )
    else:
        logger.info("UIU Smart Assistant is running on Polling mode...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
