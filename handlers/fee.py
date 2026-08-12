from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import (
    FEE_REG_CREDITS,
    FEE_RETAKE_COUNT,
    FEE_RETAKE_CREDITS,
    FEE_DISCOUNT_TYPE,
    FEE_DISCOUNT_PERCENT,
)
from keyboards import get_main_menu, get_cancel_keyboard, get_fee_discount_keyboard
from database import get_setting
from config import Config


async def fee_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fee_data"] = {}

    credit_fee = get_setting("CREDIT_FEE", Config.DEFAULT_CREDIT_FEE)
    trimester_fee = get_setting("TRIMESTER_FEE", Config.DEFAULT_TRIMESTER_FEE)

    msg = (
        "💰 **Fee Calculator**\n\n"
        f"Current Configuration:\n"
        f"• Credit Fee: {credit_fee} BDT\n"
        f"• Trimester Fee: {trimester_fee} BDT\n\n"
        "Step 1: Enter your Total Registered Credits for this trimester. (e.g., 15)"
    )
    await update.message.reply_text(
        msg, reply_markup=get_cancel_keyboard(), parse_mode="Markdown"
    )
    return FEE_REG_CREDITS


async def get_reg_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        credits = float(text)
        if credits < 0:
            raise ValueError
        context.user_data["fee_data"]["reg_credits"] = credits
        await update.message.reply_text(
            "Step 2: How many FIRST-TIME retake courses do you have? (Enter 0 if none)"
        )
        return FEE_RETAKE_COUNT
    except ValueError:
        await update.message.reply_text("⚠ Invalid input. Please enter a valid number.")
        return FEE_REG_CREDITS


async def get_retake_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        count = int(text)
        if count < 0:
            raise ValueError
        context.user_data["fee_data"]["retake_count"] = count

        if count > 0:
            context.user_data["fee_data"]["retake_credits"] = []
            context.user_data["fee_data"]["current_retake"] = 1
            await update.message.reply_text("Enter credit for Retake Course 1:")
            return FEE_RETAKE_CREDITS
        else:
            context.user_data["fee_data"]["retake_credits"] = []
            msg = "Step 3: Do you have a Scholarship or Tuition Waiver?\n*(Note: Discounts apply only to tuition fees, not the Trimester Fee)*"
            await update.message.reply_text(
                msg, reply_markup=get_fee_discount_keyboard(), parse_mode="Markdown"
            )
            return FEE_DISCOUNT_TYPE
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid input. Enter 0 or a positive integer."
        )
        return FEE_RETAKE_COUNT


async def get_retake_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        credit = float(text)
        if credit <= 0:
            raise ValueError

        context.user_data["fee_data"]["retake_credits"].append(credit)
        current = context.user_data["fee_data"]["current_retake"]
        total = context.user_data["fee_data"]["retake_count"]

        if current < total:
            context.user_data["fee_data"]["current_retake"] += 1
            await update.message.reply_text(
                f"Enter credit for Retake Course {current + 1}:"
            )
            return FEE_RETAKE_CREDITS
        else:
            msg = "Step 3: Do you have a Scholarship or Tuition Waiver?\n*(Note: Discounts apply only to tuition fees, not the Trimester Fee)*"
            await update.message.reply_text(
                msg, reply_markup=get_fee_discount_keyboard(), parse_mode="Markdown"
            )
            return FEE_DISCOUNT_TYPE
    except ValueError:
        await update.message.reply_text("⚠ Invalid credit.")
        return FEE_RETAKE_CREDITS


async def get_discount_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "⏩ None":
        context.user_data["fee_data"]["discount_type"] = "None"
        context.user_data["fee_data"]["discount_percent"] = 0
        return await calculate_fees(update, context)
    elif choice in ["🎁 Scholarship", "💸 Tuition Waiver"]:
        context.user_data["fee_data"]["discount_type"] = choice
        await update.message.reply_text(
            "Enter the percentage (e.g., 25 for 25%):",
            reply_markup=get_cancel_keyboard(),
        )
        return FEE_DISCOUNT_PERCENT
    else:
        await update.message.reply_text(
            "Please choose from the keyboard.", reply_markup=get_fee_discount_keyboard()
        )
        return FEE_DISCOUNT_TYPE


async def get_discount_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        percent = float(text)
        if not (0 <= percent <= 100):
            raise ValueError
        context.user_data["fee_data"]["discount_percent"] = percent
        return await calculate_fees(update, context)
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid percentage. Enter a number between 0 and 100."
        )
        return FEE_DISCOUNT_PERCENT


async def calculate_fees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data["fee_data"]

    credit_fee = get_setting("CREDIT_FEE", Config.DEFAULT_CREDIT_FEE)
    trimester_fee = get_setting("TRIMESTER_FEE", Config.DEFAULT_TRIMESTER_FEE)
    other_fees = get_setting("OTHER_FEES", Config.DEFAULT_OTHER_FEES)
    min_payment = get_setting("MINIMUM_PAYMENT", Config.DEFAULT_MINIMUM_PAYMENT)
    retake_discount_pct = get_setting(
        "FIRST_RETAKE_DISCOUNT_PERCENT", Config.DEFAULT_FIRST_RETAKE_DISCOUNT_PERCENT
    )
    scholarship_limit = get_setting(
        "SCHOLARSHIP_CREDIT_LIMIT", Config.DEFAULT_SCHOLARSHIP_CREDIT_LIMIT
    )

    reg_credits = data["reg_credits"]
    retake_credits_list = data.get("retake_credits", [])
    total_retake_credits = sum(retake_credits_list)

    regular_credits = reg_credits - total_retake_credits
    if regular_credits < 0:
        regular_credits = 0

    discount_type = data.get("discount_type", "None")
    discount_percent = data.get("discount_percent", 0)

    normal_tuition = regular_credits * credit_fee

    retake_tuition = (
        total_retake_credits * credit_fee * (1 - (retake_discount_pct / 100))
    )

    discount_amount = 0
    if discount_percent > 0:
        if "Scholarship" in discount_type:
            eligible_credits = min(regular_credits, scholarship_limit)
            discount_amount = (eligible_credits * credit_fee) * (discount_percent / 100)
        elif "Waiver" in discount_type:
            discount_amount = (regular_credits * credit_fee) * (discount_percent / 100)

    total_payable = (
        normal_tuition + retake_tuition + trimester_fee + other_fees - discount_amount
    )
    payment_plan = ""
    if total_payable <= min_payment:
        payment_plan = f"Registration Payment: {total_payable:,.2f} BDT\nRemaining Balance: 0.00 BDT"
    else:
        remaining = total_payable - min_payment
        inst1 = remaining * Config.INSTALLMENT_1_PERCENT
        inst2 = remaining * Config.INSTALLMENT_2_PERCENT
        inst3 = remaining * Config.INSTALLMENT_3_PERCENT
        payment_plan = (
            f"Registration Payment: {min_payment:,.2f} BDT\n"
            f"1st Installment (40%): {inst1:,.2f} BDT\n"
            f"2nd Installment (30%): {inst2:,.2f} BDT\n"
            f"3rd Installment (30%): {inst3:,.2f} BDT"
        )

    report = (
        "💰 **FEE ESTIMATE**\n\n"
        f"Registered Credits: {reg_credits}\n"
        f"Retake Credits: {total_retake_credits}\n"
        f"Credit Fee: {credit_fee} BDT\n"
        "--------------------------\n"
        f"Normal Tuition: {normal_tuition:,.2f} BDT\n"
        f"Retake Tuition: {retake_tuition:,.2f} BDT\n"
        f"Discount ({discount_type} {discount_percent}%): -{discount_amount:,.2f} BDT\n"
        f"Trimester Fee: {trimester_fee:,.2f} BDT\n"
        f"Other Fees: {other_fees:,.2f} BDT\n"
        "--------------------------\n"
        f"**Total Payable: {total_payable:,.2f} BDT**\n\n"
        "📅 **Payment Plan:**\n"
        f"{payment_plan}"
    )

    context.user_data.pop("fee_data", None)
    await update.message.reply_text(
        report, reply_markup=get_main_menu(), parse_mode="Markdown"
    )
    return ConversationHandler.END


async def fee_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("fee_data", None)
    await update.message.reply_text(
        "❌ Calculation cancelled.", reply_markup=get_main_menu()
    )
    return ConversationHandler.END
