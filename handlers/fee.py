from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from states import (
    FEE_CREDIT_FEE,
    FEE_TRIMESTER_FEE,
    FEE_REG_CREDITS,
    FEE_RETAKE_COUNT,
    FEE_RETAKE_CREDITS,
    FEE_DISCOUNT_TYPE,
    FEE_DISCOUNT_PERCENT,
)


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [["❌ Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def discount_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🎓 Scholarship"],
            ["💯 Waiver"],
            ["❌ No Discount"],
            ["❌ Cancel"],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


async def fee_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "💰 Fee Calculator\n\n" "First, enter the fee per credit.\n\n" "Example: 6500",
        reply_markup=cancel_keyboard(),
    )

    return FEE_CREDIT_FEE


async def get_credit_fee(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credit_fee = float(text)

        if credit_fee < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number.")
        return FEE_CREDIT_FEE

    context.user_data["credit_fee"] = credit_fee

    await update.message.reply_text(
        "Enter the fixed trimester/semester fee.\n\n" "Example: 5000",
        reply_markup=cancel_keyboard(),
    )

    return FEE_TRIMESTER_FEE


async def get_trimester_fee(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        trimester_fee = float(text)

        if trimester_fee < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number.")
        return FEE_TRIMESTER_FEE

    context.user_data["trimester_fee"] = trimester_fee

    await update.message.reply_text(
        "Enter your registered credits.",
        reply_markup=cancel_keyboard(),
    )

    return FEE_REG_CREDITS


async def get_reg_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credits = float(text)

        if credits < 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number.")
        return FEE_REG_CREDITS

    context.user_data["reg_credits"] = credits

    await update.message.reply_text(
        "How many retake courses do you have?",
        reply_markup=cancel_keyboard(),
    )

    return FEE_RETAKE_COUNT


async def get_retake_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("⚠️ Please enter a valid whole number.")
        return FEE_RETAKE_COUNT

    count = int(text)

    if count < 0:
        await update.message.reply_text("⚠️ Retake course count cannot be negative.")
        return FEE_RETAKE_COUNT

    context.user_data["retake_count"] = count

    if count == 0:
        context.user_data["retake_credits"] = 0

        await update.message.reply_text(
            "Select your discount type.",
            reply_markup=discount_keyboard(),
        )

        return FEE_DISCOUNT_TYPE

    context.user_data["retake_index"] = 1
    context.user_data["retake_credits"] = 0

    await update.message.reply_text(
        "Enter credit for Retake Course 1.",
        reply_markup=cancel_keyboard(),
    )

    return FEE_RETAKE_CREDITS


async def get_retake_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credit = float(text)

        if credit <= 0:
            raise ValueError

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid credit.")
        return FEE_RETAKE_CREDITS

    context.user_data["retake_credits"] += credit

    current = context.user_data["retake_index"]
    total = context.user_data["retake_count"]

    if current < total:
        context.user_data["retake_index"] += 1

        await update.message.reply_text(
            f"Enter credit for Retake Course {current + 1}.",
            reply_markup=cancel_keyboard(),
        )

        return FEE_RETAKE_CREDITS

    await update.message.reply_text(
        "Select your discount type.",
        reply_markup=discount_keyboard(),
    )

    return FEE_DISCOUNT_TYPE


async def get_discount_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if text == "❌ No Discount":
        context.user_data["discount_percent"] = 0
        return await calculate_fee(update, context)

    if text in ["🎓 Scholarship", "💯 Waiver"]:
        context.user_data["discount_type"] = text

        await update.message.reply_text(
            "Enter discount percentage.\n\n" "Example: 25",
            reply_markup=cancel_keyboard(),
        )

        return FEE_DISCOUNT_PERCENT

    await update.message.reply_text(
        "⚠️ Please select one of the available options.",
        reply_markup=discount_keyboard(),
    )

    return FEE_DISCOUNT_TYPE


async def get_discount_percent(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        percent = float(text)

        if percent < 0 or percent > 100:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a percentage between 0 and 100."
        )
        return FEE_DISCOUNT_PERCENT

    context.user_data["discount_percent"] = percent

    return await calculate_fee(update, context)


async def calculate_fee(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    credit_fee = context.user_data.get("credit_fee", 0)
    trimester_fee = context.user_data.get("trimester_fee", 0)
    reg_credits = context.user_data.get("reg_credits", 0)
    retake_credits = context.user_data.get("retake_credits", 0)
    discount_percent = context.user_data.get(
        "discount_percent",
        0,
    )

    regular_fee = reg_credits * credit_fee
    retake_fee = retake_credits * credit_fee

    subtotal = regular_fee + retake_fee + trimester_fee

    discount = subtotal * discount_percent / 100

    total = subtotal - discount

    await update.message.reply_text(
        "🎉 Fee Calculation Complete\n\n"
        f"💵 Credit Fee: ৳{credit_fee:,.2f}\n"
        f"🏫 Fixed Semester Fee: ৳{trimester_fee:,.2f}\n"
        f"📚 Registered Credits: {reg_credits:.2f}\n"
        f"🔁 Retake Credits: {retake_credits:.2f}\n\n"
        f"📌 Regular Fee: ৳{regular_fee:,.2f}\n"
        f"📌 Retake Fee: ৳{retake_fee:,.2f}\n"
        f"📌 Subtotal: ৳{subtotal:,.2f}\n"
        f"🎓 Discount: {discount_percent:.2f}%\n"
        f"💸 Discount Amount: ৳{discount:,.2f}\n\n"
        f"💰 Total Estimated Fee: ৳{total:,.2f}",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📚 CGPA Calculator", "💰 Fee Calculator"],
                ["🎁 Scholarship Calculator", "📖 Academic Info"],
                ["🔗 Important Links", "📅 Academic Calendar"],
                ["📢 Notices", "❓ Help"],
                ["⚙️ Settings", "👤 About"],
            ],
            resize_keyboard=True,
        ),
    )

    context.user_data.clear()

    return ConversationHandler.END


async def fee_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text("❌ Fee calculation cancelled.")

    return ConversationHandler.END
