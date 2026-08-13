from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from states import (
    CGPA_MENU_CHOICE,
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
)

GRADE_POINTS = {
    "A": 4.00,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.00,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.00,
    "C-": 1.67,
    "D+": 1.33,
    "D": 1.00,
    "F": 0.00,
}


def grade_keyboard():
    keyboard = [
        ["A", "A-"],
        ["B+", "B"],
        ["B-", "C+"],
        ["C", "C-"],
        ["D+", "D"],
        ["F"],
        ["❌ Cancel"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def cgpa_keyboard():
    keyboard = [
        ["➕ New Calculation"],
        ["❌ Cancel"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
    )


async def cgpa_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "📚 CGPA Calculator\n\nChoose an option.",
        reply_markup=cgpa_keyboard(),
    )

    return CGPA_MENU_CHOICE


async def cgpa_new_calc(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "📊 New CGPA Calculation\n\n"
        "Enter your completed credits before this semester."
    )

    return CGPA_PREV_CREDITS


async def get_prev_credits(
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
        return CGPA_PREV_CREDITS

    context.user_data["previous_credits"] = credits

    await update.message.reply_text("Enter your current CGPA before this semester.")

    return CGPA_PREV_CGPA


async def get_prev_cgpa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        cgpa = float(text)

        if cgpa < 0 or cgpa > 4:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid CGPA between 0.00 and 4.00."
        )
        return CGPA_PREV_CGPA

    context.user_data["previous_cgpa"] = cgpa

    await update.message.reply_text("How many courses did you complete this semester?")

    return CGPA_COURSE_COUNT


async def get_course_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("⚠️ Please enter a valid whole number.")
        return CGPA_COURSE_COUNT

    count = int(text)

    if count <= 0:
        await update.message.reply_text("⚠️ Course count must be greater than 0.")
        return CGPA_COURSE_COUNT

    context.user_data["course_count"] = count
    context.user_data["current_course"] = 1
    context.user_data["courses"] = []

    await update.message.reply_text("Enter credit for Course 1.")

    return CGPA_COURSE_CREDIT


async def get_course_credit(
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
        return CGPA_COURSE_CREDIT

    context.user_data["current_credit"] = credit

    await update.message.reply_text(
        f"Select Grade for Course " f"{context.user_data['current_course']}.",
        reply_markup=grade_keyboard(),
    )

    return CGPA_COURSE_GRADE


async def get_course_grade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    grade = update.message.text.strip().upper()

    if grade not in GRADE_POINTS:
        await update.message.reply_text(
            "⚠️ Please select a valid grade.",
            reply_markup=grade_keyboard(),
        )
        return CGPA_COURSE_GRADE

    credit = context.user_data["current_credit"]

    context.user_data["courses"].append(
        {
            "credit": credit,
            "grade": grade,
            "point": GRADE_POINTS[grade],
        }
    )

    current = context.user_data["current_course"]
    total = context.user_data["course_count"]

    if current < total:
        context.user_data["current_course"] += 1

        await update.message.reply_text(
            f"✅ Course {current} saved.\n\n" f"Enter credit for Course {current + 1}.",
            reply_markup=ReplyKeyboardMarkup(
                [["❌ Cancel"]],
                resize_keyboard=True,
            ),
        )

        return CGPA_COURSE_CREDIT

    previous_credits = context.user_data["previous_credits"]
    previous_cgpa = context.user_data["previous_cgpa"]

    semester_credits = sum(course["credit"] for course in context.user_data["courses"])

    semester_quality_points = sum(
        course["credit"] * course["point"] for course in context.user_data["courses"]
    )

    semester_gpa = (
        semester_quality_points / semester_credits if semester_credits > 0 else 0
    )

    previous_quality_points = previous_credits * previous_cgpa

    total_credits = previous_credits + semester_credits

    total_quality_points = previous_quality_points + semester_quality_points

    overall_cgpa = total_quality_points / total_credits if total_credits > 0 else 0

    await update.message.reply_text(
        "🎉 CGPA Calculation Complete\n\n"
        f"📚 Previous Credits: {previous_credits:.2f}\n"
        f"📊 Previous CGPA: {previous_cgpa:.2f}\n\n"
        f"📘 Semester Credits: {semester_credits:.2f}\n"
        f"⭐ Semester GPA: {semester_gpa:.2f}\n\n"
        f"🎓 Total Credits: {total_credits:.2f}\n"
        f"🏆 Overall CGPA: {overall_cgpa:.2f}",
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


async def cgpa_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text("❌ CGPA calculation cancelled.")

    return ConversationHandler.END
