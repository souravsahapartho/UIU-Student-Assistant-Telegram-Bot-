from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import (
    CGPA_MENU_CHOICE,
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
)
from keyboards import (
    get_main_menu,
    get_cancel_keyboard,
    get_cgpa_start_keyboard,
    get_grade_keyboard,
)

# GPA Scale mapping
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
NON_GPA_GRADES = ["I", "W", "R"]


async def cgpa_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **CGPA Calculator**\nChoose an option:",
        reply_markup=get_cgpa_start_keyboard(),
        parse_mode="Markdown",
    )
    return CGPA_MENU_CHOICE


async def cgpa_new_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize state
    context.user_data["cgpa_data"] = {}
    await update.message.reply_text(
        "Step 1: Enter your previously completed credits. (e.g., 45)\nIf you are in your first semester, enter 0.",
        reply_markup=get_cancel_keyboard(),
    )
    return CGPA_PREV_CREDITS


async def get_prev_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        credits = float(text)
        if credits < 0:
            raise ValueError
        context.user_data["cgpa_data"]["prev_credits"] = credits

        if credits == 0:
            context.user_data["cgpa_data"]["prev_cgpa"] = 0.0
            await update.message.reply_text(
                "Step 3: How many courses are you taking this semester?"
            )
            return CGPA_COURSE_COUNT
        else:
            await update.message.reply_text(
                "Step 2: Enter your current CGPA. (e.g., 3.42)"
            )
            return CGPA_PREV_CGPA
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid input. Please enter a positive number for credits."
        )
        return CGPA_PREV_CREDITS


async def get_prev_cgpa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        cgpa = float(text)
        if not (0 <= cgpa <= 4.0):
            raise ValueError
        context.user_data["cgpa_data"]["prev_cgpa"] = cgpa
        await update.message.reply_text(
            "Step 3: How many courses are you taking this semester?"
        )
        return CGPA_COURSE_COUNT
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid CGPA. Please enter a number between 0 and 4.00."
        )
        return CGPA_PREV_CGPA


async def get_course_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        count = int(text)
        if not (1 <= count <= 30):
            raise ValueError
        context.user_data["cgpa_data"]["course_count"] = count
        context.user_data["cgpa_data"]["current_course"] = 1
        context.user_data["cgpa_data"]["courses"] = []

        await update.message.reply_text(
            "Course 1:\nEnter credit for Course 1. (e.g., 3)"
        )
        return CGPA_COURSE_CREDIT
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid input. Please enter a valid number of courses (1-30)."
        )
        return CGPA_COURSE_COUNT


async def get_course_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        credit = float(text)
        if credit <= 0:
            raise ValueError
        context.user_data["cgpa_data"]["temp_credit"] = credit

        c_num = context.user_data["cgpa_data"]["current_course"]
        await update.message.reply_text(
            f"Select grade for Course {c_num}:", reply_markup=get_grade_keyboard()
        )
        return CGPA_COURSE_GRADE
    except ValueError:
        await update.message.reply_text(
            "⚠ Invalid credit. Please enter a positive number."
        )
        return CGPA_COURSE_CREDIT


async def get_course_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    grade = update.message.text
    if grade not in GRADE_POINTS and grade not in NON_GPA_GRADES:
        await update.message.reply_text(
            "⚠ Invalid grade. Please select from the keyboard.",
            reply_markup=get_grade_keyboard(),
        )
        return CGPA_COURSE_GRADE

    credit = context.user_data["cgpa_data"]["temp_credit"]
    context.user_data["cgpa_data"]["courses"].append({"credit": credit, "grade": grade})

    current = context.user_data["cgpa_data"]["current_course"]
    total = context.user_data["cgpa_data"]["course_count"]

    if current < total:
        context.user_data["cgpa_data"]["current_course"] += 1
        await update.message.reply_text(
            f"Course {current + 1}:\nEnter credit for Course {current + 1}. (e.g., 3)",
            reply_markup=get_cancel_keyboard(),
        )
        return CGPA_COURSE_CREDIT
    else:
        # Calculate CGPA
        return await calculate_final_cgpa(update, context)


async def calculate_final_cgpa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data.get("cgpa_data", {})
    prev_credits = data.get("prev_credits", 0)
    prev_cgpa = data.get("prev_cgpa", 0)
    courses = data.get("courses", [])

    semester_gpa_credits = 0.0
    semester_quality_points = 0.0
    total_semester_credits = 0.0  # Includes I, W, R

    for c in courses:
        total_semester_credits += c["credit"]
        if c["grade"] not in NON_GPA_GRADES:
            semester_gpa_credits += c["credit"]
            semester_quality_points += c["credit"] * GRADE_POINTS[c["grade"]]

    semester_gpa = (
        semester_quality_points / semester_gpa_credits
        if semester_gpa_credits > 0
        else 0.0
    )

    prev_quality_points = prev_credits * prev_cgpa
    overall_quality_points = prev_quality_points + semester_quality_points
    overall_credits = prev_credits + semester_gpa_credits

    updated_cgpa = (
        overall_quality_points / overall_credits if overall_credits > 0 else 0.0
    )

    report = (
        "🎓 **CGPA REPORT**\n\n"
        f"Previous Credits: {prev_credits:.2f}\n"
        f"Previous CGPA: {prev_cgpa:.2f}\n"
        "--------------------------\n"
        f"Semester Credits (Total): {total_semester_credits:.2f}\n"
        f"Semester GPA Credits: {semester_gpa_credits:.2f}\n"
        f"Semester GPA: {semester_gpa:.2f}\n"
        "--------------------------\n"
        f"Overall Credits: {overall_credits:.2f}\n"
        f"**Updated CGPA: {updated_cgpa:.2f}**\n\n"
        "*(Note: I, W, and R grades are excluded from GPA calculation)*"
    )

    context.user_data.pop("cgpa_data", None)
    await update.message.reply_text(
        report, reply_markup=get_main_menu(), parse_mode="Markdown"
    )
    return ConversationHandler.END


async def cgpa_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("cgpa_data", None)
    await update.message.reply_text(
        "❌ Calculation cancelled.", reply_markup=get_main_menu()
    )
    return ConversationHandler.END
