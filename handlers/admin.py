from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from database import get_setting, update_setting


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in Config.ADMIN_USER_IDS:
        await update.message.reply_text(
            "❌ You are not authorized to access the admin panel."
        )
        return

    # Extract command arguments
    args = context.args
    if not args:
        help_text = (
            "🛠 **Admin Commands**\n\n"
            "Use `/admin set <KEY> <VALUE>` to update settings.\n"
            "Available Keys:\n"
            "• CREDIT_FEE\n"
            "• TRIMESTER_FEE\n"
            "• OTHER_FEES\n"
            "• MINIMUM_PAYMENT\n\n"
            "Example: `/admin set CREDIT_FEE 6500`\n\n"
            "Use `/admin view` to see current settings."
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")
        return

    if args[0].lower() == "view":
        c_fee = get_setting("CREDIT_FEE", Config.DEFAULT_CREDIT_FEE)
        t_fee = get_setting("TRIMESTER_FEE", Config.DEFAULT_TRIMESTER_FEE)
        min_p = get_setting("MINIMUM_PAYMENT", Config.DEFAULT_MINIMUM_PAYMENT)

        msg = f"⚙️ **Current Settings:**\nCREDIT_FEE = {c_fee}\nTRIMESTER_FEE = {t_fee}\nMINIMUM_PAYMENT = {min_p}"
        await update.message.reply_text(msg, parse_mode="Markdown")

    elif args[0].lower() == "set" and len(args) == 3:
        key = args[1].upper()
        value = args[2]
        try:
            val_float = float(value)
            update_setting(key, val_float)
            await update.message.reply_text(
                f"✅ Successfully updated {key} to {val_float}"
            )
        except ValueError:
            await update.message.reply_text("❌ Value must be a number.")
    else:
        await update.message.reply_text("❌ Invalid command format.")
