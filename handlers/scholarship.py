from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from services.scholarship_service import (
    generate_estimate,
    generate_result_text,
    generate_ineligible_text,
    scholarship_rules_text,
)

SCHOLARSHIP_GPA = 500
SCHOLARSHIP_PROGRAM = 501
SCHOLARSHIP_SIZE = 502
SCHOLARSHIP_CREDITS = 503
SCHOLARSHIP_HIGHER_CHOICE = 504
SCHOLARSHIP_HIGHER_COUNT = 505


PROGRAM_OPTIONS = [
    "BBA",
    "BBA in AIS",
    "BSECO",
    "BSCSE",
    "BSEEE",
    "BSDS",
    "B.Sc. in CE",
    "BSSEDS",
    "BSSMSJ",
    "BA in English",
    "B.Pharm",
    "BSBGE",
    "Graduate",
]


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [
            [
                "❌ Cancel",
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def program_keyboard():
    rows = []

    current = []

    for program in PROGRAM_OPTIONS:
        current.append(program)

        if len(current) == 2:
            rows.append(current)
            current = []

    if current:
        rows.append(current)

    rows.append(
        [
            "❌ Cancel",
        ]
    )

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def higher_choice_keyboard():
    return ReplyKeyboardMarkup(
        [
            [
                "📊 I have an estimate",
            ],
            [
                "🤷 I don't know",
            ],
            [
                "❌ Cancel",
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def result_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔄 Calculate Again",
                    callback_data="scholarship_again",
                ),
            ],
            [
                InlineKeyboardButton(
                    "📚 Scholarship Rules",
                    callback_data="scholarship_rules",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🏠 Main Menu",
                    callback_data="scholarship_main_menu",
                ),
            ],
        ]
    )


async def scholarship_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["scholarship_data"] = {}

    await update.message.reply_text(
        "🎓 <b>Scholarship Chance Estimator</b>\n\n"
        "Let's estimate your merit scholarship chances.\n\n"
        "⚠️ This is an estimate, not an official UIU "
        "scholarship decision.\n\n"
        "Step 1 of 4\n\n"
        "Enter your <b>previous trimester/semester GPA</b>.\n\n"
        "Example: <code>3.78</code>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )

    return SCHOLARSHIP_GPA


async def scholarship_gpa(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        gpa = float(text)

        if gpa < 0 or gpa > 4:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid GPA between "
            "<b>0.00</b> and <b>4.00</b>.\n\n"
            "Example: <code>3.78</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

        return SCHOLARSHIP_GPA

    context.user_data["scholarship_data"]["gpa"] = gpa

    if gpa < 3.50:
        from services.scholarship_service import (
            generate_ineligible_text,
            validate_eligibility,
        )

        eligibility = validate_eligibility(
            gpa,
            "Unknown",
            0,
        )

        await update.message.reply_text(
            generate_ineligible_text(eligibility),
            parse_mode="HTML",
        )

        await update.message.reply_text(
            "You can start a new estimate whenever you want.",
            reply_markup=cancel_keyboard(),
        )

        return SCHOLARSHIP_GPA

    await update.message.reply_text(
        "Step 2 of 4\n\n" "🎓 <b>Select your program:</b>",
        reply_markup=program_keyboard(),
        parse_mode="HTML",
    )

    return SCHOLARSHIP_PROGRAM


async def scholarship_program(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    program = update.message.text.strip()

    if program == "❌ Cancel":
        return await scholarship_cancel(
            update,
            context,
        )

    if program not in PROGRAM_OPTIONS:
        await update.message.reply_text(
            "Please select a program from the keyboard.",
            reply_markup=program_keyboard(),
        )

        return SCHOLARSHIP_PROGRAM

    context.user_data["scholarship_data"]["program"] = program

    await update.message.reply_text(
        "Step 3 of 4\n\n"
        "👥 Approximately how many students are "
        "in your program?\n\n"
        "Example: <code>500</code>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )

    return SCHOLARSHIP_SIZE


async def scholarship_size(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        size = int(text)

        if size < 10 or size > 100000:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a reasonable student count.\n\n"
            "Example: <code>500</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

        return SCHOLARSHIP_SIZE

    context.user_data["scholarship_data"]["total_students"] = size

    program = context.user_data["scholarship_data"]["program"]

    from services.scholarship_service import (
        get_minimum_credits,
    )

    minimum_credits = get_minimum_credits(program)

    await update.message.reply_text(
        "📚 <b>Qualifying Credits</b>\n\n"
        f"How many credits did you register in the "
        f"qualifying trimester/semester?\n\n"
        f"Minimum required for <b>{program}</b>: "
        f"<b>{minimum_credits:g}</b> credits\n\n"
        "Example: <code>12</code>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )

    return SCHOLARSHIP_CREDITS


async def scholarship_credits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        credits = float(text)

        if credits <= 0 or credits > 40:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid credit amount.\n\n" "Example: <code>12</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

        return SCHOLARSHIP_CREDITS

    context.user_data["scholarship_data"]["qualifying_credits"] = credits

    await update.message.reply_text(
        "Step 4 of 4\n\n"
        "📊 Do you have an idea how many students "
        "may have a higher GPA than you?",
        reply_markup=higher_choice_keyboard(),
    )

    return SCHOLARSHIP_HIGHER_CHOICE


async def scholarship_higher_choice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    choice = update.message.text.strip()

    if choice == "📊 I have an estimate":
        await update.message.reply_text(
            "Approximately how many students do you "
            "think may have a higher GPA than you?\n\n"
            "Example: <code>20</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

        return SCHOLARSHIP_HIGHER_COUNT

    if choice == "🤷 I don't know":
        context.user_data["scholarship_data"]["higher_students"] = None

        return await calculate_scholarship(
            update,
            context,
        )

    if choice == "❌ Cancel":
        return await scholarship_cancel(
            update,
            context,
        )

    await update.message.reply_text(
        "Please choose one of the available options.",
        reply_markup=higher_choice_keyboard(),
    )

    return SCHOLARSHIP_HIGHER_CHOICE


async def scholarship_higher_count(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text.strip()

    try:
        higher = int(text)

        total_students = context.user_data["scholarship_data"]["total_students"]

        if higher < 0 or higher >= total_students:
            raise ValueError

    except ValueError:
        await update.message.reply_text(
            "⚠️ Please enter a valid number of students.\n\n"
            "The number cannot be negative or equal to/"
            "greater than the total program size.",
            reply_markup=cancel_keyboard(),
        )

        return SCHOLARSHIP_HIGHER_COUNT

    context.user_data["scholarship_data"]["higher_students"] = higher

    return await calculate_scholarship(
        update,
        context,
    )


async def calculate_scholarship(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = context.user_data.get(
        "scholarship_data",
        {},
    )

    result = generate_estimate(
        gpa=data.get("gpa"),
        program=data.get("program"),
        total_students=data.get("total_students"),
        qualifying_credits=data.get("qualifying_credits"),
        higher_students=data.get("higher_students"),
    )

    if not result.get("eligible"):
        text = generate_ineligible_text(
            result.get(
                "eligibility",
                {},
            )
        )

        await update.message.reply_text(
            text,
            parse_mode="HTML",
        )

        await update.message.reply_text(
            "You can start another estimate whenever you want.",
            reply_markup=cancel_keyboard(),
        )

        return SCHOLARSHIP_GPA

    await update.message.reply_text(
        generate_result_text(result),
        reply_markup=result_keyboard(),
        parse_mode="HTML",
    )

    context.user_data.pop(
        "scholarship_data",
        None,
    )

    return ConversationHandler.END


async def scholarship_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "scholarship_rules":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back to Result",
                        callback_data="scholarship_back",
                    )
                ]
            ]
        )

        await query.edit_message_text(
            scholarship_rules_text(),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        return

    if query.data == "scholarship_back":
        await query.edit_message_text(
            "🎓 <b>Scholarship Estimate</b>\n\n"
            "Use <b>🔄 Calculate Again</b> below "
            "to create a new estimate.",
            reply_markup=result_keyboard(),
            parse_mode="HTML",
        )

        return

    if query.data == "scholarship_again":
        await query.message.reply_text(
            "🎓 <b>Scholarship Chance Estimator</b>\n\n"
            "Enter your previous trimester/semester GPA.\n\n"
            "Example: <code>3.78</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

        return

    if query.data == "scholarship_main_menu":
        from keyboards import get_main_menu

        await query.message.reply_text(
            "🏠 Main Menu",
            reply_markup=get_main_menu(),
        )


async def scholarship_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    from keyboards import get_main_menu

    context.user_data.pop(
        "scholarship_data",
        None,
    )

    await update.message.reply_text(
        "❌ Scholarship estimation cancelled.",
        reply_markup=get_main_menu(),
    )

    return ConversationHandler.END
