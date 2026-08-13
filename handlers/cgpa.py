from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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


# These grades are not included in GPA calculation.
NON_GPA_GRADES = {
    "I",
    "W",
    "R",
}


# ============================================================
# START KEYBOARD
#
# Only the FIRST CGPA screen gets these two buttons.
#
# 📚 Grading System
# ❌ Cancel
# ============================================================


def get_cgpa_start_keyboard():

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


# ============================================================
# OTHER STEP KEYBOARD
#
# Every step after the first one gets ONLY Cancel.
# ============================================================


def get_cgpa_cancel_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "❌ Cancel",
                    callback_data="cgpa_cancel_button",
                )
            ]
        ]
    )


# ============================================================
# GRADING SYSTEM TABLE
# ============================================================


def get_grading_system_text():

    return (
        "📚 <b>UIU Grading System</b>\n\n"
        "<pre>"
        "Letter  Grade Point  Marks (%)  Assessment\n"
        "────────────────────────────────────────────\n"
        "A       4.00         90–100     Outstanding\n"
        "A-      3.67         86–89      Excellent\n"
        "B+      3.33         82–85      Very Good\n"
        "B       3.00         78–81      Good\n"
        "B-      2.67         74–77      Above Average\n"
        "C+      2.33         70–73      Average\n"
        "C       2.00         66–69      Below Average\n"
        "C-      1.67         62–65      Poor\n"
        "D+      1.33         58–61      Very Poor\n"
        "D       1.00         55–57      Pass\n"
        "F       0.00         0–54       Fail\n"
        "</pre>"
    )


# ============================================================
# START CGPA CALCULATOR
# ============================================================


async def cgpa_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    # Clear any previous calculation
    context.user_data.pop(
        "cgpa_data",
        None,
    )

    context.user_data["cgpa_data"] = {
        "courses": [],
        "current_course": 1,
    }

    # --------------------------------------------------------
    # IMPORTANT:
    # Remove the persistent Main Menu keyboard.
    # --------------------------------------------------------

    await update.message.reply_text(
        "🎓 <b>CGPA Calculator</b>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    # --------------------------------------------------------
    # FIRST SCREEN:
    # Grading System + Cancel
    # --------------------------------------------------------

    await update.message.reply_text(
        "Step 1: Enter your previously completed credits.\n\n"
        "Example: <code>45</code>\n\n"
        "If you are in your first semester, enter <code>0</code>.",
        reply_markup=get_cgpa_start_keyboard(),
        parse_mode="HTML",
    )

    return CGPA_PREV_CREDITS


# ============================================================
# PREVIOUS COMPLETED CREDITS
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
            reply_markup=get_cgpa_cancel_keyboard(),
        )

        return CGPA_PREV_CREDITS

    # --------------------------------------------------------
    # First semester
    # --------------------------------------------------------

    if credits == 0:

        context.user_data["cgpa_data"]["prev_cgpa"] = 0.0

        await update.message.reply_text(
            "Step 2: How many courses are you " "taking this semester?",
            reply_markup=get_cgpa_cancel_keyboard(),
        )

        return CGPA_COURSE_COUNT

    # --------------------------------------------------------
    # Existing student
    # --------------------------------------------------------

    await update.message.reply_text(
        "Step 2: Enter your current CGPA.\n\n" "Example: <code>3.42</code>",
        reply_markup=get_cgpa_cancel_keyboard(),
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
            reply_markup=get_cgpa_cancel_keyboard(),
        )

        return CGPA_PREV_CGPA

    await update.message.reply_text(
        "Step 3: How many courses are you " "taking this semester?",
        reply_markup=get_cgpa_cancel_keyboard(),
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
            reply_markup=get_cgpa_cancel_keyboard(),
        )

        return CGPA_COURSE_COUNT

    await update.message.reply_text(
        "Course 1:\n\n" "Enter the credit for Course 1.\n\n" "Example: <code>3</code>",
        reply_markup=get_cgpa_cancel_keyboard(),
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
            reply_markup=get_cgpa_cancel_keyboard(),
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

    # Save course
    data["courses"].append(
        {
            "course": current_course,
            "credit": credit,
            "grade": grade,
        }
    )

    # --------------------------------------------------------
    # More courses remain
    # --------------------------------------------------------

    if current_course < course_count:

        next_course = current_course + 1

        data["current_course"] = next_course

        await update.message.reply_text(
            f"Course {next_course}:\n\n"
            f"Enter the credit for Course {next_course}.\n\n"
            "Example: <code>3</code>",
            reply_markup=get_cgpa_cancel_keyboard(),
            parse_mode="HTML",
        )

        return CGPA_COURSE_CREDIT

    # --------------------------------------------------------
    # All courses completed
    # --------------------------------------------------------

    return await calculate_final_cgpa(
        update,
        context,
    )


# ============================================================
# FINAL CGPA CALCULATION
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

    semester_gpa_credits = 0.0

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

        semester_gpa_credits += credit

        semester_quality_points += credit * grade_point

    # --------------------------------------------------------
    # Semester GPA
    # --------------------------------------------------------

    if semester_gpa_credits > 0:

        semester_gpa = semester_quality_points / semester_gpa_credits

    else:

        semester_gpa = 0.0

    # --------------------------------------------------------
    # Previous quality points
    # --------------------------------------------------------

    previous_quality_points = previous_credits * previous_cgpa

    # --------------------------------------------------------
    # Overall CGPA
    # --------------------------------------------------------

    overall_quality_points = previous_quality_points + semester_quality_points

    overall_credits = previous_credits + semester_gpa_credits

    if overall_credits > 0:

        updated_cgpa = overall_quality_points / overall_credits

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
        f"{overall_credits:.2f}\n"
        f"🎓 <b>Updated CGPA: "
        f"{updated_cgpa:.2f}</b>\n\n"
        "ℹ️ I, W and R grades are excluded "
        "from GPA calculation."
    )

    # Clear calculation
    context.user_data.pop(
        "cgpa_data",
        None,
    )

    # Restore Main Menu
    await update.message.reply_text(
        result,
        reply_markup=get_main_menu(),
        parse_mode="HTML",
    )

    return ConversationHandler.END


# ============================================================
# GRADING SYSTEM CALLBACK
# ============================================================


async def cgpa_grading_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    await query.message.reply_text(
        get_grading_system_text(),
        parse_mode="HTML",
    )


# ============================================================
# CANCEL CALLBACK
# ============================================================


async def cgpa_cancel_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    await query.answer()

    # Clear current calculation
    context.user_data.pop(
        "cgpa_data",
        None,
    )

    # Remove buttons from the old message
    try:

        await query.edit_message_reply_markup(reply_markup=None)

    except Exception:
        pass

    # Return Main Menu
    await query.message.reply_text(
        "❌ CGPA calculation cancelled.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END


# ============================================================
# TEXT / COMMAND CANCEL
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
        "❌ CGPA calculation cancelled.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END
