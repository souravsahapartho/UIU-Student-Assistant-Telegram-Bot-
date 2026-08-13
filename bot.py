import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

from config import Config

from database import (
    init_db,
    get_notification_users,
    get_setting,
    update_setting,
)

from states import (
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
    FEE_ACADEMIC_SYSTEM,
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
    academic_info_callback,
    settings_menu,
    settings_callback,
    notices,
)

from handlers.cgpa import (
    cgpa_start,
    cgpa_grading_callback,
    get_prev_credits,
    get_prev_cgpa,
    get_course_count,
    get_course_credit,
    get_course_grade,
    cgpa_cancel,
)

from handlers.fee import (
    fee_start,
    get_academic_system,
    get_credit_fee,
    get_trimester_fee,
    get_reg_credits,
    get_retake_count,
    get_retake_credits,
    get_discount_type,
    get_discount_percent,
    fee_cancel,
)

from handlers.calendar import (
    academic_calendar,
)

from handlers.admin import (
    admin_panel,
)

from services.calendar_service import (
    sync_calendars,
)

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format=("%(asctime)s - %(name)s - " "%(levelname)s - %(message)s"),
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# WEBHOOK
# ============================================================

WEBHOOK_PATH = "/telegram/webhook"

WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET",
    "",
)


# ============================================================
# TELEGRAM APPLICATION
# ============================================================

telegram_app = Application.builder().token(Config.BOT_TOKEN).build()


# ============================================================
# ACADEMIC CALENDAR NOTIFICATION
# ============================================================


async def send_calendar_notifications(
    context: ContextTypes.DEFAULT_TYPE,
    new_items,
    updated_items,
):

    users = get_notification_users()

    if not users:
        return

    # --------------------------------------------------------
    # New calendars
    # --------------------------------------------------------

    for calendar in new_items:

        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        url = calendar.get(
            "url",
            "",
        )

        text = (
            "🔔 <b>New Academic Calendar</b>\n\n"
            f"📅 {title}\n\n"
            "UIU has published a new academic calendar."
        )

        keyboard = []

        if url:

            keyboard.append(
                [
                    InlineKeyboardButton(
                        "📄 View Calendar",
                        url=url,
                    )
                ]
            )

        markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        for telegram_id in users:

            try:

                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode="HTML",
                )

            except Exception as error:

                logger.warning(
                    "New calendar notification failed " "for %s: %s",
                    telegram_id,
                    error,
                )

    # --------------------------------------------------------
    # Updated calendars
    # --------------------------------------------------------

    for calendar in updated_items:

        title = calendar.get(
            "title",
            "Academic Calendar",
        )

        url = calendar.get(
            "url",
            "",
        )

        text = (
            "🔄 <b>Academic Calendar Updated</b>\n\n"
            f"📅 {title}\n\n"
            "UIU has updated this academic calendar."
        )

        keyboard = []

        if url:

            keyboard.append(
                [
                    InlineKeyboardButton(
                        "📄 View Updated Calendar",
                        url=url,
                    )
                ]
            )

        markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        for telegram_id in users:

            try:

                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode="HTML",
                )

            except Exception as error:

                logger.warning(
                    "Updated calendar notification failed " "for %s: %s",
                    telegram_id,
                    error,
                )


# ============================================================
# CALENDAR UPDATE JOB
# ============================================================


async def calendar_update_job(
    context: ContextTypes.DEFAULT_TYPE,
):

    try:

        initialized = get_setting(
            "CALENDAR_INITIALIZED",
            0,
        )

        result = await sync_calendars()

        new_items = result.get(
            "new",
            [],
        )

        updated_items = result.get(
            "updated",
            [],
        )

        # ----------------------------------------------------
        # First sync:
        # Do NOT notify everyone about old calendars.
        # ----------------------------------------------------

        if not initialized:

            update_setting(
                "CALENDAR_INITIALIZED",
                1,
            )

            logger.info("Academic calendar initialized " "without notification.")

            return

        if not new_items and not updated_items:

            return

        await send_calendar_notifications(
            context,
            new_items,
            updated_items,
        )

    except Exception as error:

        logger.error(
            "Academic calendar sync failed: %s",
            error,
            exc_info=True,
        )


# ============================================================
# CGPA CONVERSATION
# ============================================================


def create_cgpa_handler():

    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^🎓 CGPA Calculator$"),
                cgpa_start,
            )
        ],
        states={
            # ------------------------------------------------
            # Previous Credits
            # ------------------------------------------------
            CGPA_PREV_CREDITS: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(r"^❌ Cancel$")
                    & ~filters.Regex(r"^📚 Grading System$"),
                    get_prev_credits,
                )
            ],
            # ------------------------------------------------
            # Previous CGPA
            # ------------------------------------------------
            CGPA_PREV_CGPA: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(r"^❌ Cancel$")
                    & ~filters.Regex(r"^📚 Grading System$"),
                    get_prev_cgpa,
                )
            ],
            # ------------------------------------------------
            # Course Count
            # ------------------------------------------------
            CGPA_COURSE_COUNT: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(r"^❌ Cancel$")
                    & ~filters.Regex(r"^📚 Grading System$"),
                    get_course_count,
                )
            ],
            # ------------------------------------------------
            # Course Credit
            # ------------------------------------------------
            CGPA_COURSE_CREDIT: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(r"^❌ Cancel$")
                    & ~filters.Regex(r"^📚 Grading System$"),
                    get_course_credit,
                )
            ],
            # ------------------------------------------------
            # Course Grade
            # ------------------------------------------------
            CGPA_COURSE_GRADE: [
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(r"^❌ Cancel$")
                    & ~filters.Regex(r"^📚 Grading System$"),
                    get_course_grade,
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                cgpa_cancel,
            ),
            MessageHandler(
                filters.Regex(r"^❌ Cancel$"),
                cgpa_cancel,
            ),
            MessageHandler(
                filters.Regex(r"^📚 Grading System$"),
                cgpa_grading_callback,
            ),
        ],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )


# ============================================================
# FEE CONVERSATION
# ============================================================


def create_fee_handler():

    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(r"^💰 Fee Calculator$"),
                fee_start,
            )
        ],
        states={
            FEE_ACADEMIC_SYSTEM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_academic_system,
                )
            ],
            FEE_CREDIT_FEE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_credit_fee,
                )
            ],
            FEE_TRIMESTER_FEE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_trimester_fee,
                )
            ],
            FEE_REG_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_reg_credits,
                )
            ],
            FEE_RETAKE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_retake_count,
                )
            ],
            FEE_RETAKE_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_retake_credits,
                )
            ],
            FEE_DISCOUNT_TYPE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_discount_type,
                )
            ],
            FEE_DISCOUNT_PERCENT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & ~filters.Regex(r"^❌ Cancel$"),
                    get_discount_percent,
                )
            ],
        },
        fallbacks=[
            CommandHandler(
                "cancel",
                fee_cancel,
            ),
            MessageHandler(
                filters.Regex(r"^❌ Cancel$"),
                fee_cancel,
            ),
        ],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )


# ============================================================
# SETUP HANDLERS
# ============================================================


def setup_handlers():

    # --------------------------------------------------------
    # CGPA
    # --------------------------------------------------------

    telegram_app.add_handler(create_cgpa_handler())

    # --------------------------------------------------------
    # Fee
    # --------------------------------------------------------

    telegram_app.add_handler(create_fee_handler())

    # ========================================================
    # COMMANDS
    # ========================================================

    telegram_app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    telegram_app.add_handler(
        CommandHandler(
            "help",
            show_help,
        )
    )

    telegram_app.add_handler(
        CommandHandler(
            "admin",
            admin_panel,
        )
    )

    # ========================================================
    # MAIN MENU
    # ========================================================

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^📚 Academic Info$"),
            academic_info,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^🔗 Important Links$"),
            show_links,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^📢 Notices$"),
            notices,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^📅 Academic Calendar$"),
            academic_calendar,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^❓ Help$"),
            show_help,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^⚙️ Settings$"),
            settings_menu,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^👤 About$"),
            show_about,
        )
    )

    # --------------------------------------------------------
    # Scholarship
    # --------------------------------------------------------

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^🎁 Scholarship Calculator$"),
            show_not_implemented,
        )
    )

    # --------------------------------------------------------
    # Global Cancel
    # --------------------------------------------------------

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex(r"^❌ Cancel$"),
            handle_cancel,
        )
    )

    # --------------------------------------------------------
    # Academic Info callbacks
    # --------------------------------------------------------

    telegram_app.add_handler(
        CallbackQueryHandler(
            academic_info_callback,
            pattern=r"^acad_",
        )
    )

    # --------------------------------------------------------
    # Settings callbacks
    # --------------------------------------------------------

    telegram_app.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern=r"^toggle_alerts$",
        )
    )


# ============================================================
# ERROR HANDLER
# ============================================================


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

    logger.error(
        "Telegram update error",
        exc_info=context.error,
    )


# ============================================================
# LIFESPAN
# ============================================================


@asynccontextmanager
async def lifespan(
    fastapi_app: FastAPI,
):

    Config.validate()

    init_db()

    setup_handlers()

    telegram_app.add_error_handler(error_handler)

    # --------------------------------------------------------
    # Start Telegram application
    # --------------------------------------------------------

    await telegram_app.initialize()

    await telegram_app.start()

    # --------------------------------------------------------
    # Calendar checker
    # --------------------------------------------------------

    if telegram_app.job_queue:

        telegram_app.job_queue.run_repeating(
            calendar_update_job,
            interval=1800,
            first=60,
            name="academic-calendar-check",
        )

        logger.info("Academic calendar checker started.")

    else:

        logger.error("JobQueue is unavailable.")

    # --------------------------------------------------------
    # Render URL
    # --------------------------------------------------------

    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if not render_url:

        raise RuntimeError("RENDER_EXTERNAL_URL is not available.")

    # --------------------------------------------------------
    # Webhook
    # --------------------------------------------------------

    webhook_url = render_url.rstrip("/") + WEBHOOK_PATH

    webhook_args = {
        "url": webhook_url,
        "drop_pending_updates": True,
    }

    if WEBHOOK_SECRET:

        webhook_args["secret_token"] = WEBHOOK_SECRET

    await telegram_app.bot.set_webhook(**webhook_args)

    logger.info(
        "Webhook configured: %s",
        webhook_url,
    )

    logger.info("UIU Smart Assistant is running.")

    yield

    # ========================================================
    # SHUTDOWN
    # ========================================================

    try:

        await telegram_app.bot.delete_webhook()

    except Exception as error:

        logger.warning(
            "Webhook delete failed: %s",
            error,
        )

    try:

        await telegram_app.stop()

    except Exception as error:

        logger.warning(
            "Telegram application stop failed: %s",
            error,
        )

    try:

        await telegram_app.shutdown()

    except Exception as error:

        logger.warning(
            "Telegram application shutdown failed: %s",
            error,
        )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="UIU Smart Assistant",
    lifespan=lifespan,
)


# ============================================================
# ROOT
# ============================================================


@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "UIU Smart Assistant",
    }


# ============================================================
# HEALTH
# ============================================================


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "telegram": "webhook",
        "academic_calendar": "active",
    }


# ============================================================
# TELEGRAM WEBHOOK
# ============================================================


@app.post(WEBHOOK_PATH)
async def telegram_webhook(
    request: Request,
):

    # --------------------------------------------------------
    # Verify secret if configured
    # --------------------------------------------------------

    if WEBHOOK_SECRET:

        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if received_secret != WEBHOOK_SECRET:

            raise HTTPException(
                status_code=403,
                detail="Invalid webhook secret",
            )

    try:

        data = await request.json()

        update = Update.de_json(
            data,
            telegram_app.bot,
        )

        if update is not None:

            # Immediate HTTP response to Telegram.
            asyncio.create_task(telegram_app.process_update(update))

        return {"ok": True}

    except Exception as error:

        logger.error(
            "Webhook processing error: %s",
            error,
            exc_info=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed",
        )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    port = int(
        os.getenv(
            "PORT",
            "10000",
        )
    )

    uvicorn.run(
        "bot:app",
        host="0.0.0.0",
        port=port,
    )
