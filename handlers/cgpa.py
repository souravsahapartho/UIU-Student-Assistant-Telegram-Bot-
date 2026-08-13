from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from states import (
    CGPA_PREV_CREDITS,
    CGPA_PREV_CGPA,
    CGPA_COURSE_COUNT,
    CGPA_COURSE_CREDIT,
    CGPA_COURSE_GRADE,
)

from keyboards import (
    get_main_menu,
    get_grade_keyboard,
)

# ============================================================
# UIU GRADE POINTS
# ============================================================

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


NON_GPA_GRADES = {
    "I",
    "W",
    "R",
}


# ============================================================
# CGPA FIXED KEYBOARD
#
# This keyboard stays at the bottom of Telegram.
#
# 📚 Grading System
# ❌ Cancel
# ============================================================


def get_cgpa_keyboard():

    return ReplyKeyboardMarkup(
        [
            [
                "📚 Grading System",
            ],
            [
                "❌ Cancel",
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


# ============================================================
# GRADING SYSTEM TEXT
# ============================================================


def get_grading_system_text():

    return (
        "📚 <b>UIU Grading System</b>\n\n"
        "<pre>"
        "Letter  Grade Point  Marks (%)\n"
        "──────────────────────────────\n"
        "A       4.00         90–100\n"
        "A-      3.67         86–89\n"
        "B+      3.33         82–85\n"
        "B       3.00         78–81\n"
        "B-      2.67         74–77\n"
        "C+      2.33         70–73\n"
        "C       2.00         66–69\n"
        "C-      1.67         62–65\n"
        "D+      1.33         58–61\n"
        "D       1.00         55–57\n"
        "F       0.00         0–54\n"
        "</pre>"
    )


# ============================================================
# CGPA START
# ============================================================


async def cgpa_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # Clear old calculation
    context.user_data.pop(
        "cgpa_data",
        None,
    )

    context.user_data["cgpa_data"] = {
        "courses": [],
        "current_course": 1,
    }

    # --------------------------------------------------------
    # Remove Main Menu
    # --------------------------------------------------------

    await update.message.reply_text(
        "🎓 <b>CGPA Calculator</b>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    # --------------------------------------------------------
    # Show fixed CGPA keyboard
    # --------------------------------------------------------

    await update.message.reply_text(
        "Step 1: Enter your previously completed credits.\n\n"
        "Example: <code>45</code>\n\n"
        "If you are in your first semester, enter <code>0</code>.",
        reply_markup=get_cgpa_keyboard(),
        parse_mode="HTML",
    )

    return CGPA_PREV_CREDITS


# ============================================================
# PREVIOUS CREDITS
# ============================================================


async def get_prev_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text.strip()

    try:

        credits = float(text)

        if credits < 0:
            raise ValueError

        context.user_data["cgpa_data"]["prev_credits"] = credits

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid input.\n\n" "Please enter a valid number.\n\n" "Example: 45",
        )

        return CGPA_PREV_CREDITS

    # --------------------------------------------------------
    # First semester
    # --------------------------------------------------------

    if credits == 0:

        context.user_data["cgpa_data"]["prev_cgpa"] = 0.0

        await update.message.reply_text(
            "Step 2: How many courses are you " "taking this semester?",
        )

        return CGPA_COURSE_COUNT

    # --------------------------------------------------------
    # Existing student
    # --------------------------------------------------------

    await update.message.reply_text(
        "Step 2: Enter your current CGPA.\n\n" "Example: <code>3.42</code>",
        parse_mode="HTML",
    )

    return CGPA_PREV_CGPA


# ============================================================
# PREVIOUS CGPA
# ============================================================


async def get_prev_cgpa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text.strip()

    try:

        cgpa = float(text)

        if cgpa < 0 or cgpa > 4.00:
            raise ValueError

        context.user_data["cgpa_data"]["prev_cgpa"] = cgpa

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid CGPA.\n\n"
            "Please enter a value between "
            "0.00 and 4.00.\n\n"
            "Example: 3.42",
        )

        return CGPA_PREV_CGPA

    await update.message.reply_text(
        "Step 3: How many courses are you " "taking this semester?",
    )

    return CGPA_COURSE_COUNT


# ============================================================
# COURSE COUNT
# ============================================================


async def get_course_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text.strip()

    try:

        count = int(text)

        if count < 1 or count > 30:
            raise ValueError

        context.user_data["cgpa_data"]["course_count"] = count

        context.user_data["cgpa_data"]["current_course"] = 1

        context.user_data["cgpa_data"]["courses"] = []

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid number of courses.\n\n"
            "Please enter a number between 1 and 30.",
        )

        return CGPA_COURSE_COUNT

    await update.message.reply_text(
        "Course 1:\n\n" "Enter the credit for Course 1.\n\n" "Example: <code>3</code>",
        parse_mode="HTML",
    )

    return CGPA_COURSE_CREDIT


# ============================================================
# COURSE CREDIT
# ============================================================


async def get_course_credit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text.strip()

    try:

        credit = float(text)

        if credit <= 0 or credit > 20:
            raise ValueError

        context.user_data["cgpa_data"]["temp_credit"] = credit

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid credit.\n\n"
            "Please enter a valid positive number.\n\n"
            "Example: 3",
        )

        return CGPA_COURSE_CREDIT

    course_number = context.user_data["cgpa_data"]["current_course"]

    await update.message.reply_text(
        f"Course {course_number}:\n\n" "Select the grade:",
        reply_markup=get_grade_keyboard(),
    )

    return CGPA_COURSE_GRADE


# ============================================================
# COURSE GRADE
# ============================================================


async def get_course_grade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    grade = update.message.text.strip().upper()

    if grade not in GRADE_POINTS and grade not in NON_GPA_GRADES:

        await update.message.reply_text(
            "⚠️ Invalid grade.\n\n" "Please select a valid grade.",
            reply_markup=get_grade_keyboard(),
        )

        return CGPA_COURSE_GRADE

    data = context.user_data["cgpa_data"]

    credit = data["temp_credit"]

    current_course = data["current_course"]

    course_count = data["course_count"]

    data["courses"].append(
        {
            "course": current_course,
            "credit": credit,
            "grade": grade,
        }
    )

    # --------------------------------------------------------
    # More courses
    # --------------------------------------------------------

    if current_course < course_count:

        next_course = current_course + 1

        data["current_course"] = next_course

        await update.message.reply_text(
            f"Course {next_course}:\n\n"
            f"Enter the credit for Course {next_course}.\n\n"
            "Example: <code>3</code>",
            parse_mode="HTML",
        )

        return CGPA_COURSE_CREDIT

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    return await calculate_final_cgpa(
        update,
        context,
    )


# ============================================================
# CALCULATE FINAL CGPA
# ============================================================


async def calculate_final_cgpa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    data = context.user_data["cgpa_data"]

    previous_credits = data.get(
        "prev_credits",
        0.0,
    )

    previous_cgpa = data.get(
        "prev_cgpa",
        0.0,
    )

    courses = data.get(
        "courses",
        [],
    )

    semester_credits = 0.0

    semester_quality_points = 0.0

    # --------------------------------------------------------
    # Calculate semester GPA
    # --------------------------------------------------------

    for course in courses:

        credit = float(course["credit"])

        grade = course["grade"]

        if grade in NON_GPA_GRADES:
            continue

        grade_point = GRADE_POINTS.get(
            grade,
            0.0,
        )

        semester_credits += credit

        semester_quality_points += credit * grade_point

    # --------------------------------------------------------
    # Semester GPA
    # --------------------------------------------------------

    if semester_credits > 0:

        semester_gpa = semester_quality_points / semester_credits

    else:

        semester_gpa = 0.0

    # --------------------------------------------------------
    # Previous quality points
    # --------------------------------------------------------

    previous_quality_points = previous_credits * previous_cgpa

    # --------------------------------------------------------
    # Overall CGPA
    # --------------------------------------------------------

    total_quality_points = previous_quality_points + semester_quality_points

    total_credits = previous_credits + semester_credits

    if total_credits > 0:

        updated_cgpa = total_quality_points / total_credits

    else:

        updated_cgpa = 0.0

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    result = (
        "🎓 <b>CGPA Calculation Result</b>\n\n"
        f"📊 Previous Credits: "
        f"{previous_credits:.2f}\n"
        f"📈 Previous CGPA: "
        f"{previous_cgpa:.2f}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📚 Semester Credits: "
        f"{semester_credits:.2f}\n"
        f"🎯 Semester GPA: "
        f"{semester_gpa:.2f}\n\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Total Credits: "
        f"{total_credits:.2f}\n"
        f"🎓 <b>Updated CGPA: "
        f"{updated_cgpa:.2f}</b>\n\n"
        "ℹ️ I, W and R grades are excluded "
        "from GPA calculation."
    )

    context.user_data.pop(
        "cgpa_data",
        None,
    )

    # --------------------------------------------------------
    # Return Main Menu
    # --------------------------------------------------------

    await update.message.reply_text(
        result,
        reply_markup=get_main_menu(),
        parse_mode="HTML",
    )

    return ConversationHandler.END


# ============================================================
# GRADING SYSTEM
#
# This is a Reply Keyboard button.
# It works during the whole CGPA calculation.
# ============================================================


async def cgpa_grading_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # This function handles the text button:
    # "📚 Grading System"

    await update.message.reply_text(
        get_grading_system_text(),
        parse_mode="HTML",
        reply_markup=get_cgpa_keyboard(),
    )

    return None


# ============================================================
# CANCEL
# ============================================================


async def cgpa_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data.pop(
        "cgpa_data",
        None,
    )

    await update.message.reply_text(
        "❌ CGPA calculation cancelled.\n\n" "Returning to the main menu.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END
