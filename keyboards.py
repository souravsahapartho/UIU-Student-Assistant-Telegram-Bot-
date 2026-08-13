from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_menu():
    keyboard = [
        [
            KeyboardButton("🎓 CGPA Calculator"),
            KeyboardButton("💰 Fee Calculator"),
        ],
        [
            KeyboardButton("🎁 Scholarship Calculator"),
            KeyboardButton("📚 Academic Info"),
        ],
        [
            KeyboardButton("🔗 Important Links"),
            KeyboardButton("📅 Academic Calendar"),
        ],
        [
            KeyboardButton("📢 Notices"),
            KeyboardButton("❓ Help"),
        ],
        [
            KeyboardButton("⚙️ Settings"),
            KeyboardButton("👤 About"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_academic_info_menu():
    keyboard = [
        [
            KeyboardButton("🎓 Admission"),
            KeyboardButton("📝 Registration"),
        ],
        [
            KeyboardButton("📊 Credit System"),
            KeyboardButton("🔄 Retake Rules"),
        ],
        [
            KeyboardButton("🎯 Graduation"),
            KeyboardButton("📚 Grading System"),
        ],
        [
            KeyboardButton("⬅️ Main Menu"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("❌ Cancel")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_cgpa_start_keyboard():
    keyboard = [
        [KeyboardButton("📚 Grading System")],
        [KeyboardButton("❌ Cancel")],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_grade_keyboard():
    keyboard = [
        [
            KeyboardButton("A"),
            KeyboardButton("A-"),
            KeyboardButton("B+"),
            KeyboardButton("B"),
        ],
        [
            KeyboardButton("B-"),
            KeyboardButton("C+"),
            KeyboardButton("C"),
            KeyboardButton("C-"),
        ],
        [
            KeyboardButton("D+"),
            KeyboardButton("D"),
            KeyboardButton("F"),
        ],
        [
            KeyboardButton("I"),
            KeyboardButton("W"),
            KeyboardButton("R"),
        ],
        [KeyboardButton("❌ Cancel")],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_links_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "eLMS",
                url="https://elms.uiu.ac.bd",
            ),
            InlineKeyboardButton(
                "UCAM",
                url="https://ucam.uiu.ac.bd",
            ),
        ],
        [
            InlineKeyboardButton(
                "UCAM Cloud",
                url="https://uiu.ucamcloud.com",
            ),
            InlineKeyboardButton(
                "Official Website",
                url="https://www.uiu.ac.bd",
            ),
        ],
        [
            InlineKeyboardButton(
                "Library",
                url="https://library.uiu.ac.bd",
            ),
            InlineKeyboardButton(
                "CSE Dept",
                url="https://cse.uiu.ac.bd",
            ),
        ],
        [
            InlineKeyboardButton(
                "CSE Projects",
                url="https://cse.uiu.ac.bd/projects",
            ),
            InlineKeyboardButton(
                "Cisco / CENTeR",
                url="https://cisco.uiu.ac.bd",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_fee_discount_keyboard():
    keyboard = [
        [
            KeyboardButton("🎁 Scholarship"),
            KeyboardButton("💸 Tuition Waiver"),
        ],
        [
            KeyboardButton("⏩ None"),
            KeyboardButton("❌ Cancel"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )
