from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from states import (
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

    credit_fee = get_setting(
        "CREDIT_FEE",
        Config.DEFAULT_CREDIT_FEE,
    )

    trimester_fee = get_setting(
        "TRIMESTER_FEE",
        Config.DEFAULT_TRIMESTER_FEE,
    )

    context.user_data["fee_data"]["credit_fee"] = credit_fee
    context.user_data["fee_data"]["trimester_fee"] = trimester_fee

    await update.message.reply_text(
        "💰 **Fee Calculator**\n\n"
        f"Credit Fee: {credit_fee:,.2f} BDT\n"
        f"Trimester Fee: {trimester_fee:,.2f} BDT\n\n"
        "Step 1: Enter your Total Registered Credits for this trimester.\n"
        "Example: 15",
        reply_markup=get_cancel_keyboard(),
        parse_mode="Markdown",
    )

    return FEE_REG_CREDITS


async def get_reg_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credits = float(text)

        if credits <= 0:
            raise ValueError

        context.user_data["fee_data"]["reg_credits"] = credits

        await update.message.reply_text(
            "Step 2: How many **FIRST-TIME retake courses** do you have?\n\n"
            "First-time retake = the course is being retaken for the first time.\n"
            "Enter 0 if you have none.",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown",
        )

        context.user_data["fee_data"]["retake_stage"] = "first"

        return FEE_RETAKE_COUNT

    except ValueError:
        await update.message.reply_text(
            "⚠️ Invalid input.\n\n" "Please enter a valid positive number."
        )

        return FEE_REG_CREDITS


async def get_retake_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        count = int(text)

        if count < 0:
            raise ValueError

        data = context.user_data["fee_data"]
        stage = data.get("retake_stage", "first")

        if stage == "first":
            data["first_retake_count"] = count
            data["first_retake_credits"] = []
            data["current_retake"] = 1

            if count > 0:
                await update.message.reply_text(
                    "Enter credit for **First-Time Retake Course 1:**",
                    reply_markup=get_cancel_keyboard(),
                    parse_mode="Markdown",
                )

                return FEE_RETAKE_CREDITS

            data["retake_stage"] = "repeat"

            await update.message.reply_text(
                "Step 3: How many **SECOND-TIME OR SUBSEQUENT retake courses** "
                "do you have?\n\n"
                "These retakes receive **no retake discount**.\n"
                "Enter 0 if you have none.",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_COUNT

        data["repeat_retake_count"] = count
        data["repeat_retake_credits"] = []
        data["current_retake"] = 1

        if count > 0:
            await update.message.reply_text(
                "Enter credit for **Second-Time/Subsequent Retake Course 1:**",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_CREDITS

        await update.message.reply_text(
            "Step 4: Do you have a Scholarship or Tuition Waiver?\n\n"
            "⚠️ Scholarship/Waiver applies only to **regular course tuition**.\n"
            "Retake courses are not eligible for Scholarship or Tuition Waiver.",
            reply_markup=get_fee_discount_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_DISCOUNT_TYPE

    except ValueError:
        await update.message.reply_text(
            "⚠️ Invalid input.\n\n" "Please enter 0 or a positive integer."
        )

        return FEE_RETAKE_COUNT


async def get_retake_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credit = float(text)

        if credit <= 0:
            raise ValueError

        data = context.user_data["fee_data"]
        stage = data.get("retake_stage", "first")

        if stage == "first":
            data["first_retake_credits"].append(credit)

            current = data["current_retake"]
            total = data["first_retake_count"]

            if current < total:
                data["current_retake"] += 1

                await update.message.reply_text(
                    f"Enter credit for **First-Time Retake Course {current + 1}:**",
                    reply_markup=get_cancel_keyboard(),
                    parse_mode="Markdown",
                )

                return FEE_RETAKE_CREDITS

            data["retake_stage"] = "repeat"
            data["current_retake"] = 1

            await update.message.reply_text(
                "Step 3: How many **SECOND-TIME OR SUBSEQUENT retake courses** "
                "do you have?\n\n"
                "These retakes receive **no discount**.\n"
                "Enter 0 if you have none.",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_COUNT

        data["repeat_retake_credits"].append(credit)

        current = data["current_retake"]
        total = data["repeat_retake_count"]

        if current < total:
            data["current_retake"] += 1

            await update.message.reply_text(
                f"Enter credit for "
                f"**Second-Time/Subsequent Retake Course {current + 1}:**",
                reply_markup=get_cancel_keyboard(),
                parse_mode="Markdown",
            )

            return FEE_RETAKE_CREDITS

        await update.message.reply_text(
            "Step 4: Do you have a Scholarship or Tuition Waiver?\n\n"
            "⚠️ Scholarship/Waiver applies only to **regular course tuition**.\n"
            "Retake courses are not eligible for Scholarship or Tuition Waiver.",
            reply_markup=get_fee_discount_keyboard(),
            parse_mode="Markdown",
        )

        return FEE_DISCOUNT_TYPE

    except ValueError:
        await update.message.reply_text(
            "⚠️ Invalid credit.\n\n" "Please enter a valid positive number."
        )

        return FEE_RETAKE_CREDITS


async def get_discount_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    choice = update.message.text.strip()

    if choice == "⏩ None":
        context.user_data["fee_data"]["discount_type"] = "None"
        context.user_data["fee_data"]["discount_percent"] = 0

        return await calculate_fees(update, context)

    if choice in ["🎁 Scholarship", "💸 Tuition Waiver"]:
        context.user_data["fee_data"]["discount_type"] = choice

        await update.message.reply_text(
            "Enter the discount percentage.\n\n" "Example: 25 for 25%",
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
    text = update.message.text.strip()

    try:
        percent = float(text)

        if percent < 0 or percent > 100:
            raise ValueError

        context.user_data["fee_data"]["discount_percent"] = percent

        return await calculate_fees(update, context)

    except ValueError:
        await update.message.reply_text(
            "⚠️ Invalid percentage.\n\n" "Enter a number between 0 and 100."
        )

        return FEE_DISCOUNT_PERCENT


async def calculate_fees(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = context.user_data["fee_data"]

    credit_fee = data.get(
        "credit_fee",
        get_setting(
            "CREDIT_FEE",
            Config.DEFAULT_CREDIT_FEE,
        ),
    )

    trimester_fee = data.get(
        "trimester_fee",
        get_setting(
            "TRIMESTER_FEE",
            Config.DEFAULT_TRIMESTER_FEE,
        ),
    )

    other_fees = get_setting(
        "OTHER_FEES",
        Config.DEFAULT_OTHER_FEES,
    )

    min_payment = get_setting(
        "MINIMUM_PAYMENT",
        Config.DEFAULT_MINIMUM_PAYMENT,
    )

    scholarship_limit = get_setting(
        "SCHOLARSHIP_CREDIT_LIMIT",
        Config.DEFAULT_SCHOLARSHIP_CREDIT_LIMIT,
    )

    first_retake_discount = 50

    reg_credits = data.get("reg_credits", 0)

    first_retake_credits_list = data.get(
        "first_retake_credits",
        [],
    )

    repeat_retake_credits_list = data.get(
        "repeat_retake_credits",
        [],
    )

    first_retake_credits = sum(first_retake_credits_list)

    repeat_retake_credits = sum(repeat_retake_credits_list)

    total_retake_credits = first_retake_credits + repeat_retake_credits

    regular_credits = reg_credits - total_retake_credits

    if regular_credits < 0:
        regular_credits = 0

    regular_tuition = regular_credits * credit_fee

    first_retake_normal_tuition = first_retake_credits * credit_fee

    first_retake_discount_amount = (
        first_retake_normal_tuition * first_retake_discount / 100
    )

    first_retake_tuition = first_retake_normal_tuition - first_retake_discount_amount

    repeat_retake_tuition = repeat_retake_credits * credit_fee

    discount_type = data.get(
        "discount_type",
        "None",
    )

    discount_percent = data.get(
        "discount_percent",
        0,
    )

    scholarship_waiver_discount = 0

    if discount_percent > 0:
        if "Scholarship" in discount_type:
            eligible_credits = min(
                regular_credits,
                scholarship_limit,
            )

            scholarship_waiver_discount = (
                eligible_credits * credit_fee * discount_percent / 100
            )

        elif "Waiver" in discount_type:
            scholarship_waiver_discount = (
                regular_credits * credit_fee * discount_percent / 100
            )

    total_tuition = regular_tuition + first_retake_tuition + repeat_retake_tuition

    total_discount = first_retake_discount_amount + scholarship_waiver_discount

    total_payable = total_tuition + trimester_fee + other_fees

    if total_payable <= min_payment:
        registration_payment = total_payable
        remaining_balance = 0

        payment_plan = (
            f"Registration Payment: "
            f"{registration_payment:,.2f} BDT\n"
            f"Remaining Balance: 0.00 BDT"
        )

    else:
        registration_payment = min_payment
        remaining_balance = total_payable - registration_payment

        inst1 = remaining_balance * Config.INSTALLMENT_1_PERCENT

        inst2 = remaining_balance * Config.INSTALLMENT_2_PERCENT

        inst3 = remaining_balance * Config.INSTALLMENT_3_PERCENT

        payment_plan = (
            f"Registration Payment: "
            f"{registration_payment:,.2f} BDT\n"
            f"1st Installment (40%): "
            f"{inst1:,.2f} BDT\n"
            f"2nd Installment (30%): "
            f"{inst2:,.2f} BDT\n"
            f"3rd Installment (30%): "
            f"{inst3:,.2f} BDT"
        )

    report = (
        "💰 **FEE ESTIMATE**\n\n"
        f"Registered Credits: {reg_credits:,.2f}\n"
        f"Regular Credits: {regular_credits:,.2f}\n"
        f"First-Time Retake Credits: "
        f"{first_retake_credits:,.2f}\n"
        f"Subsequent Retake Credits: "
        f"{repeat_retake_credits:,.2f}\n"
        f"Total Retake Credits: "
        f"{total_retake_credits:,.2f}\n\n"
        f"Credit Fee: {credit_fee:,.2f} BDT\n"
        f"Trimester Fee: {trimester_fee:,.2f} BDT\n"
        "--------------------------\n"
        f"Regular Tuition: "
        f"{regular_tuition:,.2f} BDT\n"
        f"First-Time Retake Tuition: "
        f"{first_retake_tuition:,.2f} BDT\n"
        f"Subsequent Retake Tuition: "
        f"{repeat_retake_tuition:,.2f} BDT\n"
        "--------------------------\n"
        f"First-Time Retake Discount (50%): "
        f"-{first_retake_discount_amount:,.2f} BDT\n"
        f"{discount_type} Discount on Regular Tuition: "
        f"-{scholarship_waiver_discount:,.2f} BDT\n"
        "--------------------------\n"
        f"Other Fees: {other_fees:,.2f} BDT\n"
        f"**Total Payable: {total_payable:,.2f} BDT**\n\n"
        "ℹ️ Retake courses are not eligible for "
        "Scholarship or Tuition Waiver.\n"
        "ℹ️ Subsequent retakes receive no retake discount.\n\n"
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
