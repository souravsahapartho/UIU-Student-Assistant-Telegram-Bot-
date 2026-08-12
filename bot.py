\import os
import asyncio
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from config import Config
from handlers.general import (
    start, help_command, about, academic_info,
    important_links, notices, academic_calendar,
    academic_info_callback
)
from handlers.cgpa import (
    cgpa_start, cgpa_new_calc, get_prev_credits, get_prev_cgpa,
    get_course_count, get_course_credit, get_course_grade, cgpa_cancel
)
from handlers.fee import (
    fee_start, get_reg_credits, get_retake_courses,
    get_retake_credits, get_scholarship, get_waiver, fee_cancel
)
from handlers.admin import (
    admin_panel, set_config, admin_broadcast, broadcast_message
)
from states import (
    CGPA_MENU_CHOICE, CGPA_PREV_CREDITS, CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT, CGPA_COURSE_CREDIT, CGPA_COURSE_GRADE,
    FEE_REG_CREDITS, FEE_RETAKE_COUNT, FEE_RETAKE_CREDITS,
    FEE_SCHOLARSHIP, FEE_WAIVER,
    ADMIN_BROADCAST_MESSAGE
)
from database import init_db

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    load_dotenv()
    init_db()

    app = Application.builder().token(Config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("set", set_config))

    cgpa_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎓 CGPA Calculator$"), cgpa_start)],
        states={
            CGPA_MENU_CHOICE: [MessageHandler(filters.Regex("^➕ New Calculation$"), cgpa_new_calc)],
            CGPA_PREV_CREDITS: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_prev_credits)],
            CGPA_PREV_CGPA: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_prev_cgpa)],
            CGPA_COURSE_COUNT: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_count)],
            CGPA_COURSE_CREDIT: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_credit)],
            CGPA_COURSE_GRADE: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_course_grade)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Cancel$"), cgpa_cancel), CommandHandler("cancel", cgpa_cancel)],
        per_user=True
    )
    app.add_handler(cgpa_conv_handler)

    fee_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 Fee Calculator$"), fee_start)],
        states={
            FEE_REG_CREDITS: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_reg_credits)],
            FEE_RETAKE_COUNT: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_retake_courses)],
            FEE_RETAKE_CREDITS: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_retake_credits)],
            FEE_SCHOLARSHIP: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_scholarship)],
            FEE_WAIVER: [MessageHandler(filters.TEXT & ~filters.Regex("^❌ Cancel$"), get_waiver)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Cancel$"), fee_cancel), CommandHandler("cancel", fee_cancel)],
        per_user=True
    )
    app.add_handler(fee_conv_handler)

    admin_broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", admin_broadcast)],
        states={
            ADMIN_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.Command, broadcast_message)],
        },
        fallbacks=[],
        per_user=True
    )
    app.add_handler(admin_broadcast_handler)

    app.add_handler(MessageHandler(filters.Regex("^📚 Academic Information$"), academic_info))
    app.add_handler(MessageHandler(filters.Regex("^🔗 Important Links$"), important_links))
    app.add_handler(MessageHandler(filters.Regex("^📢 Notices$"), notices))
    app.add_handler(MessageHandler(filters.Regex("^📅 Academic Calendar$"), academic_calendar))
    app.add_handler(MessageHandler(filters.Regex("^❓ Help$"), help_command))
    app.add_handler(MessageHandler(filters.Regex("^👤 About$"), about))

    app.add_handler(CallbackQueryHandler(academic_info_callback, pattern="^acad_"))

    port = int(os.environ.get('PORT', 10000))
    webhook_url = os.environ.get('WEBHOOK_URL')

    if webhook_url:
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=Config.BOT_TOKEN,
            webhook_url=f"{webhook_url}/{Config.BOT_TOKEN}"
        )
    else:
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()