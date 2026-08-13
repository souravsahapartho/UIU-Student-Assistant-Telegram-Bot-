import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException

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
    CGPA_MENU_CHOICE,
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

from handlers.calendar import academic_calendar
from handlers.admin import admin_panel

from services.calendar_service import sync_calendars

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("bot")

WEBHOOK_PATH = "/telegram/webhook"

WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET",
    "",
).strip()

telegram_app = (
    Application.builder().token(Config.BOT_TOKEN).concurrent_updates(True).build()
)

_handlers_setup = False


async def send_calendar_notifications(
    context: ContextTypes.DEFAULT_TYPE,
    new_items,
    updated_items,
):
    users = get_notification_users()

    if not users:
        return

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
            "🔔 New Academic Calendar\n\n"
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
                )
            except Exception as error:
                logger.warning(
                    "New calendar notification failed for %s: %s",
                    telegram_id,
                    error,
                )

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
            "🔄 Academic Calendar Updated\n\n"
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
                )
            except Exception as error:
                logger.warning(
                    "Updated calendar notification failed for %s: %s",
                    telegram_id,
                    error,
                )


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

        if not initialized:
            update_setting(
                "CALENDAR_INITIALIZED",
                1,
            )

            logger.info("Academic calendar initialized without notification.")

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


def setup_handlers():

    global _handlers_setup

    if _handlers_setup:
        return

    cgpa_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^🎓 CGPA Calculator$"),
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
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_prev_credits,
                )
            ],
            CGPA_PREV_CGPA: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_prev_cgpa,
                )
            ],
            CGPA_COURSE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_course_count,
                )
            ],
            CGPA_COURSE_CREDIT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_course_credit,
                )
            ],
            CGPA_COURSE_GRADE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
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
        per_chat=True,
    )

    fee_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^💰 Fee Calculator$"),
                fee_start,
            )
        ],
        states={
            FEE_ACADEMIC_SYSTEM: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_academic_system,
                )
            ],
            FEE_CREDIT_FEE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_credit_fee,
                )
            ],
            FEE_TRIMESTER_FEE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_trimester_fee,
                )
            ],
            FEE_REG_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_reg_credits,
                )
            ],
            FEE_RETAKE_COUNT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_retake_count,
                )
            ],
            FEE_RETAKE_CREDITS: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_retake_credits,
                )
            ],
            FEE_DISCOUNT_TYPE: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
                    get_discount_type,
                )
            ],
            FEE_DISCOUNT_PERCENT: [
                MessageHandler(
                    filters.TEXT & ~filters.Regex("^❌ Cancel$"),
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
        per_chat=True,
    )

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

    telegram_app.add_handler(cgpa_conv_handler)

    telegram_app.add_handler(fee_conv_handler)

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^📚 Academic Info$"),
            academic_info,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^🔗 Important Links$"),
            show_links,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^📢 Notices$"),
            notices,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^📅 Academic Calendar$"),
            academic_calendar,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^❓ Help$"),
            show_help,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^⚙️ Settings$"),
            settings_menu,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^👤 About$"),
            show_about,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^❌ Cancel$"),
            handle_cancel,
        )
    )

    telegram_app.add_handler(
        MessageHandler(
            filters.Regex("^🎁 Scholarship Calculator$"),
            show_not_implemented,
        )
    )

    telegram_app.add_handler(
        CallbackQueryHandler(
            academic_info_callback,
            pattern="^acad_",
        )
    )

    telegram_app.add_handler(
        CallbackQueryHandler(
            settings_callback,
            pattern="^toggle_alerts$",
        )
    )

    _handlers_setup = True


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
                "⚠️ Something went wrong. " "Please try again or type /start."
            )
        except Exception:
            pass


async def process_telegram_update(
    update: Update,
):
    try:
        logger.info(
            "Processing Telegram update: %s",
            update.update_id,
        )

        await telegram_app.process_update(update)

        logger.info(
            "Telegram update processed successfully: %s",
            update.update_id,
        )

    except Exception as error:
        logger.error(
            "Background Telegram update processing failed: %s",
            error,
            exc_info=True,
        )


@asynccontextmanager
async def lifespan(
    fastapi_app: FastAPI,
):
    Config.validate()

    init_db()

    setup_handlers()

    telegram_app.add_error_handler(error_handler)

    await telegram_app.initialize()

    await telegram_app.start()

    if telegram_app.job_queue:
        telegram_app.job_queue.run_repeating(
            calendar_update_job,
            interval=1800,
            first=10,
            name="academic-calendar-check",
        )

        logger.info("Academic calendar checker started.")

    render_url = os.getenv("RENDER_EXTERNAL_URL")

    if not render_url:
        raise RuntimeError("RENDER_EXTERNAL_URL is not available.")

    webhook_url = render_url.rstrip("/") + WEBHOOK_PATH

    webhook_args = {
        "url": webhook_url,
        "drop_pending_updates": False,
        "allowed_updates": [
            "message",
            "callback_query",
        ],
    }

    if WEBHOOK_SECRET:
        webhook_args["secret_token"] = WEBHOOK_SECRET

    await telegram_app.bot.set_webhook(**webhook_args)

    logger.info(
        "Webhook configured: %s",
        webhook_url,
    )

    try:
        webhook_info = await telegram_app.bot.get_webhook_info()

        logger.info(
            "Webhook info: url=%s pending=%s last_error=%s",
            webhook_info.url,
            webhook_info.pending_update_count,
            webhook_info.last_error_message,
        )

    except Exception as error:
        logger.warning(
            "Could not read webhook info: %s",
            error,
        )

    logger.info("UIU Smart Assistant is running...")

    yield

    try:
        await telegram_app.stop()
    except Exception as error:
        logger.warning(
            "Telegram application stop error: %s",
            error,
        )

    try:
        await telegram_app.shutdown()
    except Exception as error:
        logger.warning(
            "Telegram application shutdown error: %s",
            error,
        )


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "UIU Smart Assistant",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "telegram": "webhook",
        "calendar_checker": "active",
    }


@app.post(WEBHOOK_PATH)
async def telegram_webhook(
    request: Request,
):
    logger.info("=== TELEGRAM WEBHOOK RECEIVED ===")

    if WEBHOOK_SECRET:
        received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        if received_secret != WEBHOOK_SECRET:
            logger.error("Invalid Telegram webhook secret")

            raise HTTPException(
                status_code=403,
                detail="Invalid webhook secret",
            )

    try:
        data = await request.json()

        update_id = data.get("update_id")

        logger.info(
            "Telegram update received: %s",
            update_id,
        )

        update = Update.de_json(
            data,
            telegram_app.bot,
        )

        if update is None:
            logger.warning("Received empty Telegram update.")

            return {"ok": True}

        asyncio.create_task(process_telegram_update(update))

        logger.info(
            "Telegram update accepted immediately: %s",
            update_id,
        )

        return {"ok": True}

    except Exception as error:
        logger.error(
            "Telegram webhook error: %s",
            error,
            exc_info=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Webhook processing failed",
        )


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
