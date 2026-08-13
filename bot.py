import asyncio
import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import Config
from database import init_db

from states import (
    CGPA_MENU_CHOICE,
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
    FEE_CREDIT_FEE,
    FEE_TRIMESTER_FEE,
    FEE_REG_CREDITS,
    FEE_RETAKE_COUNT,
    FEE_RETAKE_CREDITS,
    FEE_DISCOUNT_TYPE,
    FEE_DISCOUNT_PERCENT,
)

from handlers.general import (
    start,
    show_links,
    show_about,
    show_help,
    handle_cancel,
    show_not_implemented,
    academic_info,
    academic_calendar,
    notices,
    settings_menu,
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
    get_credit_fee,
    get_trimester_fee,
    get_reg_credits,
    get_retake_count,
    get_retake_credits,
    get_discount_type,
    get_discount_percent,
    fee_cancel,
)

from handlers.admin import admin_panel

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):
    logger.error(
        "Exception while handling an update:",
        exc_info=context.error,
    )

    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text(
                "⚠️ Something went wrong. Please try again."
            )
        except Exception:
            pass


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    Config.validate()
    init_db()

    app = Application.builder().token(Config.BOT_TOKEN).build()

    cgpa_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^📚 CGPA Calculator$"),
                cgpa_start,
            )
        ],
        states={
            CGPA_MENU_CHOICE: [
                MessageHandler(
                    filters.Regex("^➕ New Calculation$"),
                    cgpa_new_calc,
                )
            ],
            CGPA_PREV_CREDITS: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_prev_credits,
                )
            ],
            CGPA_PREV_CGPA: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_prev_cgpa,
                )
            ],
            CGPA_COURSE_COUNT: [
                MessageHandler(
                    filters.Regex(r"^\d+$"),
                    get_course_count,
                )
            ],
            CGPA_COURSE_CREDIT: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_course_credit,
                )
            ],
            CGPA_COURSE_GRADE: [
                MessageHandler(
                    filters.Regex(r"^(A|A-|B\+|B|B-|C\+|C|C-|D\+|D|F)$"),
                    get_course_grade,
                )
            ],
        },
        fallbacks=[
            MessageHandler(
                filters.Regex("^❌ Cancel$"),
                cgpa_cancel,
            ),
            CommandHandler(
                "cancel",
                cgpa_cancel,
            ),
        ],
        per_user=True,
        allow_reentry=True,
    )

    fee_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^💰 Fee Calculator$"),
                fee_start,
            )
        ],
        states={
            FEE_CREDIT_FEE: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_credit_fee,
                )
            ],
            FEE_TRIMESTER_FEE: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_trimester_fee,
                )
            ],
            FEE_REG_CREDITS: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_reg_credits,
                )
            ],
            FEE_RETAKE_COUNT: [
                MessageHandler(
                    filters.Regex(r"^\d+$"),
                    get_retake_count,
                )
            ],
            FEE_RETAKE_CREDITS: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_retake_credits,
                )
            ],
            FEE_DISCOUNT_TYPE: [
                MessageHandler(
                    filters.Regex(r"^(🎓 Scholarship|💯 Waiver|❌ No Discount)$"),
                    get_discount_type,
                )
            ],
            FEE_DISCOUNT_PERCENT: [
                MessageHandler(
                    filters.Regex(r"^\d+(?:\.\d+)?$"),
                    get_discount_percent,
                )
            ],
        },
        fallbacks=[
            MessageHandler(
                filters.Regex("^❌ Cancel$"),
                fee_cancel,
            ),
            CommandHandler(
                "cancel",
                fee_cancel,
            ),
        ],
        per_user=True,
        allow_reentry=True,
    )

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            show_help,
        )
    )

    app.add_handler(
        CommandHandler(
            "admin",
            admin_panel,
        )
    )

    app.add_handler(cgpa_conv_handler)
    app.add_handler(fee_conv_handler)

    app.add_handler(
        MessageHandler(
            filters.Regex("^🔗 Important Links$"),
            show_links,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^👤 About$"),
            show_about,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^❓ Help$"),
            show_help,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📖 Academic Info$"),
            academic_info,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📅 Academic Calendar$"),
            academic_calendar,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^📢 Notices$"),
            notices,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^⚙️ Settings$"),
            settings_menu,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^(🎁 Scholarship Calculator)$"),
            show_not_implemented,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex("^❌ Cancel$"),
            handle_cancel,
        )
    )

    app.add_error_handler(error_handler)

    print("UIU Smart Assistant is running...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
