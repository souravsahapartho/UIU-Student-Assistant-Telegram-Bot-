import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
import uvicorn
from fastapi import FastAPI, Request, Response
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
from handlers.admin import admin_panel, admin_broadcast, broadcast_message
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
    ADMIN_BROADCAST_MESSAGE,
)
from database import init_db

load_dotenv()

app = FastAPI()
ptb = Application.builder().token(Config.BOT_TOKEN).build()


@app.on_event("startup")
async def startup_event():
    init_db()

    ptb.add_handler(CommandHandler("start", start))
    ptb.add_handler(CommandHandler("help", help_command))
    ptb.add_handler(CommandHandler("about", about))
    ptb.add_handler(CommandHandler("admin", admin_panel))
    ptb.add_handler(CommandHandler("broadcast", admin_broadcast))

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
    ptb.add_handler(cgpa_conv_handler)

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
    ptb.add_handler(fee_conv_handler)

    admin_broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", admin_broadcast)],
        states={
            ADMIN_BROADCAST_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.Command, broadcast_message)
            ],
        },
        fallbacks=[],
        per_user=True,
    )
    ptb.add_handler(admin_broadcast_handler)

    ptb.add_handler(MessageHandler(filters.Regex("^📚 Academic Info$"), academic_info))
    ptb.add_handler(
        MessageHandler(filters.Regex("^🔗 Important Links$"), important_links)
    )
    ptb.add_handler(MessageHandler(filters.Regex("^📢 Notices$"), notices))
    ptb.add_handler(
        MessageHandler(filters.Regex("^📅 Academic Calendar$"), academic_calendar)
    )
    ptb.add_handler(MessageHandler(filters.Regex("^❓ Help$"), help_command))
    ptb.add_handler(MessageHandler(filters.Regex("^👤 About$"), about))
    ptb.add_handler(CallbackQueryHandler(academic_info_callback, pattern="^acad_"))

    await ptb.initialize()
    await ptb.start()

    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        await ptb.bot.set_webhook(
            url=f"{webhook_url}/{Config.BOT_TOKEN}", drop_pending_updates=True
        )


@app.on_event("shutdown")
async def shutdown_event():
    await ptb.stop()
    await ptb.shutdown()


@app.post("/{token}")
async def process_update(request: Request, token: str):
    if token == Config.BOT_TOKEN:
        update_data = await request.json()
        update = Update.de_json(update_data, ptb.bot)
        await ptb.process_update(update)
        return Response(status_code=200)
    return Response(status_code=403)


@app.get("/")
async def health_check():
    return {"status": "UIU Smart Assistant is running!"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
