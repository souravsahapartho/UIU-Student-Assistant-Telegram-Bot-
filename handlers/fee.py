from telegram import Update
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

from keyboards import (
    get_main_menu,
    get_cancel_keyboard,
    get_fee_discount_keyboard,
)

from database import get_setting
from config import Config


async def fee_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fee_data"] = {}

    await update.message.reply_text(
        "💰 **Fee Calculator**\n\n"
        "Let's calculate your semester/trimester fee.\n\n"
        "Step 1: Enter the **Credit Fee** per credit in BDT.\n"
        "Example: 6500",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )

    return FEE_CREDIT_FEE


async def get_credit_fee(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    try:
        credit_fee = float(text)

        if credit_fee <= 0:
            raise ValueError

        context.user_data["fee_data"]["credit_fee"] = credit_fee

        await update.message.reply_text(
            "Step 2: Enter the **Trimester/Semester Fee** in BDT.\n" "Example: 5000",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_TRIMESTER_FEE

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid amount.\n\n" "Please enter a valid positive number."
        )

        return FEE_CREDIT_FEE


async def get_trimester_fee(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    try:
        trimester_fee = float(text)

        if trimester_fee < 0:
            raise ValueError

        context.user_data["fee_data"]["trimester_fee"] = trimester_fee

        await update.message.reply_text(
            "Step 3: Enter your **Total Registered Credits** "
            "for this semester/trimester.\n\n"
            "Example: 15",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_REG_CREDITS

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid amount.\n\n" "Please enter a valid number."
        )

        return FEE_TRIMESTER_FEE


async def get_reg_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    try:
        credits = float(text)

        if credits < 0:
            raise ValueError

        context.user_data["fee_data"]["reg_credits"] = credits

        await update.message.reply_text(
            "Step 4: How many **FIRST-TIME retake courses** "
            "do you have?\n\n"
            "Enter 0 if you have none.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_RETAKE_COUNT

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid input.\n\n" "Please enter a valid number."
        )

        return FEE_REG_CREDITS


async def get_retake_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    try:
        count = int(text)

        if count < 0:
            raise ValueError

        context.user_data["fee_data"]["retake_count"] = count

        if count > 0:
            context.user_data["fee_data"]["retake_credits"] = []
            context.user_data["fee_data"]["current_retake"] = 1

            await update.message.reply_text(
                "Step 5: Enter credit for **Retake Course 1**.",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_CREDITS

        context.user_data["fee_data"]["retake_credits"] = []

        await update.message.reply_text(
            "Step 6: Do you have a **Scholarship or Tuition Waiver**?\n\n"
            "Discounts apply only to tuition fees, not the "
            "Trimester/Semester Fee.",
            reply_markup=get_fee_discount_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_DISCOUNT_TYPE

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid input.\n\n" "Enter 0 or a positive integer."
        )

        return FEE_RETAKE_COUNT


async def get_retake_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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
                f"Enter credit for **Retake Course {current + 1}**.",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_CREDITS

        await update.message.reply_text(
            "Step 6: Do you have a **Scholarship or Tuition Waiver**?\n\n"
            "Discounts apply only to tuition fees, not the "
            "Trimester/Semester Fee.",
            reply_markup=get_fee_discount_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_DISCOUNT_TYPE

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid credit.\n\n" "Please enter a positive number."
        )

        return FEE_RETAKE_CREDITS


async def get_discount_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    choice = update.message.text

    if choice == "⏩ None":
        context.user_data["fee_data"]["discount_type"] = "None"
        context.user_data["fee_data"]["discount_percent"] = 0

        return await calculate_fees(update, context)

    if choice in [
        "🎁 Scholarship",
        "💸 Tuition Waiver",
    ]:
        context.user_data["fee_data"]["discount_type"] = choice

        await update.message.reply_text(
            "Step 7: Enter the discount percentage.\n\n" "Example: 25 for 25%",
            reply_markup=get_cancel_keyboard(),
        )

        return FEE_DISCOUNT_PERCENT

    await update.message.reply_text(
        "Please choose an option from the keyboard.",
        reply_markup=get_fee_discount_keyboard(),
    )

    return FEE_DISCOUNT_TYPE


async def get_discount_percent(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    try:
        percent = float(text)

        if not 0 <= percent <= 100:
            raise ValueError

        context.user_data["fee_data"]["discount_percent"] = percent

        return await calculate_fees(update, context)

    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid percentage.\n\n" "Enter a number between 0 and 100."
        )

        return FEE_DISCOUNT_PERCENT


async def calculate_fees(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = context.user_data["fee_data"]

    credit_fee = data["credit_fee"]
    trimester_fee = data["trimester_fee"]

    other_fees = get_setting(
        "OTHER_FEES",
        Config.DEFAULT_OTHER_FEES,
    )

    min_payment = get_setting(
        "MINIMUM_PAYMENT",
        Config.DEFAULT_MINIMUM_PAYMENT,
    )

    retake_discount_pct = get_setting(
        "FIRST_RETAKE_DISCOUNT_PERCENT",
        Config.DEFAULT_FIRST_RETAKE_DISCOUNT_PERCENT,
    )

    scholarship_limit = get_setting(
        "SCHOLARSHIP_CREDIT_LIMIT",
        Config.DEFAULT_SCHOLARSHIP_CREDIT_LIMIT,
    )

    reg_credits = data["reg_credits"]

    retake_credits_list = data.get(
        "retake_credits",
        [],
    )

    total_retake_credits = sum(retake_credits_list)

    regular_credits = reg_credits - total_retake_credits

    if regular_credits < 0:
        regular_credits = 0

    discount_type = data.get(
        "discount_type",
        "None",
    )

    discount_percent = data.get(
        "discount_percent",
        0,
    )

    normal_tuition = regular_credits * credit_fee

    retake_tuition = (
        total_retake_credits * credit_fee * (1 - (retake_discount_pct / 100))
    )

    discount_amount = 0

    if discount_percent > 0:

        if "Scholarship" in discount_type:

            eligible_credits = min(
                regular_credits,
                scholarship_limit,
            )

            discount_amount = eligible_credits * credit_fee * (discount_percent / 100)

        elif "Waiver" in discount_type:

            discount_amount = regular_credits * credit_fee * (discount_percent / 100)

    total_payable = (
        normal_tuition + retake_tuition + trimester_fee + other_fees - discount_amount
    )

    if total_payable <= min_payment:

        payment_plan = (
            f"Registration Payment: "
            f"{total_payable:,.2f} BDT\n"
            "Remaining Balance: 0.00 BDT"
        )

    else:

        remaining = total_payable - min_payment

        inst1 = remaining * Config.INSTALLMENT_1_PERCENT

        inst2 = remaining * Config.INSTALLMENT_2_PERCENT

        inst3 = remaining * Config.INSTALLMENT_3_PERCENT

        payment_plan = (
            f"Registration Payment: "
            f"{min_payment:,.2f} BDT\n"
            f"1st Installment (40%): "
            f"{inst1:,.2f} BDT\n"
            f"2nd Installment (30%): "
            f"{inst2:,.2f} BDT\n"
            f"3rd Installment (30%): "
            f"{inst3:,.2f} BDT"
        )

    report = (
        "💰 **FEE ESTIMATE**\n\n"
        f"Registered Credits: {reg_credits}\n"
        f"Retake Credits: {total_retake_credits}\n"
        f"Credit Fee: {credit_fee:,.2f} BDT\n"
        f"Trimester/Semester Fee: "
        f"{trimester_fee:,.2f} BDT\n"
        "--------------------------\n"
        f"Normal Tuition: "
        f"{normal_tuition:,.2f} BDT\n"
        f"Retake Tuition: "
        f"{retake_tuition:,.2f} BDT\n"
        f"Discount ({discount_type} "
        f"{discount_percent}%): "
        f"-{discount_amount:,.2f} BDT\n"
        f"Other Fees: "
        f"{other_fees:,.2f} BDT\n"
        "--------------------------\n"
        f"**Total Payable: "
        f"{total_payable:,.2f} BDT**\n\n"
        "📅 **Payment Plan:**\n"
        f"{payment_plan}"
    )

    context.user_data.pop(
        "fee_data",
        None,
    )

    await update.message.reply_text(
        report,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )

    return ConversationHandler.END


async def fee_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.pop(
        "fee_data",
        None,
    )

    await update.message.reply_text(
        "❌ Calculation cancelled.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END
