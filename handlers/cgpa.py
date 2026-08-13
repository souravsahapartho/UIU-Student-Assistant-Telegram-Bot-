from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
    get_cancel_keyboard,
    get_grade_keyboard,
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

NON_GPA_GRADES = [
    "I",
    "W",
    "R",
]


def get_cgpa_input_keyboard():
    """
    Keyboard shown during CGPA calculation.

    Grading System is placed directly above Cancel.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📚 Grading System",
                    callback_data="cgpa_grading",
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="cgpa_cancel_button",
                )
            ],
        ]
    )


def grading_system_text():

    return (
        "📚 <b>UIU Grading System</b>\n\n"
        "<pre>"
        "Letter   Grade   Marks     Assessment\n"
        "────────────────────────────────────\n"
        "A        4.00    90–100    Outstanding\n"
        "A-       3.67    86–89     Excellent\n"
        "B+       3.33    82–85     Very Good\n"
        "B        3.00    78–81     Good\n"
        "B-       2.67    74–77     Above Average\n"
        "C+       2.33    70–73     Average\n"
        "C        2.00    66–69     Below Average\n"
        "C-       1.67    62–65     Poor\n"
        "D+       1.33    58–61     Very Poor\n"
        "D        1.00    55–57     Pass\n"
        "F        0.00    0–54      Fail\n"
        "</pre>"
    )


async def cgpa_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    context.user_data["cgpa_data"] = {}

    await update.message.reply_text(
        "🎓 <b>CGPA Calculator</b>\n\n"
        "Step 1: Enter your previously completed credits.\n\n"
        "Example: <code>45</code>\n\n"
        "If you are in your first semester, enter <code>0</code>.",
        reply_markup=get_cgpa_input_keyboard(),
        parse_mode="HTML",
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

        context.user_data["cgpa_data"]["prev_credits"] = credits

        if credits == 0:

            context.user_data["cgpa_data"]["prev_cgpa"] = 0.0

            await update.message.reply_text(
                "Step 2: How many courses are you " "taking this semester?",
                reply_markup=get_cgpa_input_keyboard(),
            )

            return CGPA_COURSE_COUNT

        await update.message.reply_text(
            "Step 2: Enter your current CGPA.\n\n" "Example: <code>3.42</code>",
            reply_markup=get_cgpa_input_keyboard(),
            parse_mode="HTML",
        )

        return CGPA_PREV_CGPA

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid input.\n\n"
            "Please enter a valid non-negative number "
            "for completed credits.",
            reply_markup=get_cgpa_input_keyboard(),
        )

        return CGPA_PREV_CREDITS


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

        if not 0 <= cgpa <= 4.0:
            raise ValueError

        context.user_data["cgpa_data"]["prev_cgpa"] = cgpa

        await update.message.reply_text(
            "Step 3: How many courses are you " "taking this semester?",
            reply_markup=get_cgpa_input_keyboard(),
        )

        return CGPA_COURSE_COUNT

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid CGPA.\n\n" "Please enter a number between " "0.00 and 4.00.",
            reply_markup=get_cgpa_input_keyboard(),
        )

        return CGPA_PREV_CGPA


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

        if not 1 <= count <= 30:
            raise ValueError

        context.user_data["cgpa_data"]["course_count"] = count

        context.user_data["cgpa_data"]["current_course"] = 1

        context.user_data["cgpa_data"]["courses"] = []

        await update.message.reply_text(
            "Course 1:\n" "Enter credit for Course 1.\n\n" "Example: <code>3</code>",
            reply_markup=get_cgpa_input_keyboard(),
            parse_mode="HTML",
        )

        return CGPA_COURSE_CREDIT

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid input.\n\n"
            "Please enter the number of courses "
            "between 1 and 30.",
            reply_markup=get_cgpa_input_keyboard(),
        )

        return CGPA_COURSE_COUNT


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

        if credit <= 0:
            raise ValueError

        context.user_data["cgpa_data"]["temp_credit"] = credit

        course_number = context.user_data["cgpa_data"]["current_course"]

        await update.message.reply_text(
            f"Select grade for Course {course_number}:",
            reply_markup=get_grade_keyboard(),
        )

        return CGPA_COURSE_GRADE

    except ValueError:

        await update.message.reply_text(
            "⚠️ Invalid credit.\n\n" "Please enter a positive number.",
            reply_markup=get_cgpa_input_keyboard(),
        )

        return CGPA_COURSE_CREDIT


# ============================================================
# COURSE GRADE
# ============================================================


async def get_course_grade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    grade = update.message.text.strip()

    if grade not in GRADE_POINTS and grade not in NON_GPA_GRADES:

        await update.message.reply_text(
            "⚠️ Invalid grade.\n\n" "Please select a valid grade.",
            reply_markup=get_grade_keyboard(),
        )

        return CGPA_COURSE_GRADE

    credit = context.user_data["cgpa_data"]["temp_credit"]

    context.user_data["cgpa_data"]["courses"].append(
        {
            "credit": credit,
            "grade": grade,
        }
    )

    current = context.user_data["cgpa_data"]["current_course"]

    total = context.user_data["cgpa_data"]["course_count"]

    if current < total:

        next_course = current + 1

        context.user_data["cgpa_data"]["current_course"] = next_course

        await update.message.reply_text(
            f"Course {next_course}:\n"
            f"Enter credit for Course {next_course}.\n\n"
            "Example: <code>3</code>",
            reply_markup=get_cgpa_input_keyboard(),
            parse_mode="HTML",
        )

        return CGPA_COURSE_CREDIT

    return await calculate_final_cgpa(
        update,
        context,
    )


# ============================================================
# FINAL CALCULATION
# ============================================================


async def calculate_final_cgpa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    data = context.user_data.get(
        "cgpa_data",
        {},
    )

    prev_credits = data.get(
        "prev_credits",
        0,
    )

    prev_cgpa = data.get(
        "prev_cgpa",
        0,
    )

    courses = data.get(
        "courses",
        [],
    )

    semester_gpa_credits = 0.0
    semester_quality_points = 0.0
    total_semester_credits = 0.0

    for course in courses:

        credit = course["credit"]
        grade = course["grade"]

        total_semester_credits += credit

        if grade not in NON_GPA_GRADES:

            semester_gpa_credits += credit

            semester_quality_points += credit * GRADE_POINTS[grade]

    semester_gpa = (
        semester_quality_points / semester_gpa_credits
        if semester_gpa_credits > 0
        else 0.0
    )

    previous_quality_points = prev_credits * prev_cgpa

    overall_quality_points = previous_quality_points + semester_quality_points

    overall_credits = prev_credits + semester_gpa_credits

    updated_cgpa = (
        overall_quality_points / overall_credits if overall_credits > 0 else 0.0
    )

    report = (
        "🎓 <b>CGPA REPORT</b>\n\n"
        f"Previous Credits: {prev_credits:.2f}\n"
        f"Previous CGPA: {prev_cgpa:.2f}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Semester Credits: "
        f"{total_semester_credits:.2f}\n"
        f"Semester GPA Credits: "
        f"{semester_gpa_credits:.2f}\n"
        f"Semester GPA: "
        f"{semester_gpa:.2f}\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Overall Credits: "
        f"{overall_credits:.2f}\n"
        f"<b>Updated CGPA: "
        f"{updated_cgpa:.2f}</b>\n\n"
        "ℹ️ I, W, and R grades are excluded "
        "from GPA calculation."
    )

    context.user_data.pop(
        "cgpa_data",
        None,
    )

    await update.message.reply_text(
        report,
        reply_markup=get_main_menu(),
        parse_mode="HTML",
    )

    return ConversationHandler.END


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
        "❌ Calculation cancelled.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END


# ============================================================
# GRADING SYSTEM BUTTON
# ============================================================


async def cgpa_grading_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        grading_system_text(),
        parse_mode="HTML",
    )
