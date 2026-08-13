import logging
import feedparser

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from telegram.ext import ContextTypes

from keyboards import (
    get_main_menu,
    get_links_keyboard,
)

from database import (
    log_user_activity,
    get_recent_notices,
    get_notification_status,
    toggle_notification,
)

logger = logging.getLogger(__name__)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.message.from_user

    log_user_activity(
        user.id,
        user.first_name,
        user.username,
    )

    welcome_msg = (
        f"👋 Welcome to **UIU Student Assistant**, {user.first_name}!\n\n"
        "Your personal assistant for:\n"
        "🎓 CGPA calculation\n"
        "💰 Tuition fee calculation\n"
        "🎁 Scholarship calculation\n"
        "📚 Academic resources\n"
        "🔗 Important UIU links\n"
        "📅 Academic calendar\n"
        "📢 Latest notices\n\n"
        "👨‍💻 _Made with ❤️ by @souravsahapartho_\n\n"
        "👇 Select an option from the menu below."
    )

    await update.message.reply_text(
        welcome_msg,
        reply_markup=get_main_menu(),
        parse_mode="Markdown",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    help_text = (
        "❓ **Help Center**\n\n"
        "🎓 **CGPA Calculator**\n"
        "Calculate semester GPA and updated overall CGPA.\n\n"
        "💰 **Fee Calculator**\n"
        "Estimate tuition fees, retake fees, scholarships, "
        "waivers and installments.\n\n"
        "🎁 **Scholarship Calculator**\n"
        "Estimate your merit scholarship chances based on "
        "your academic information.\n\n"
        "📚 **Academic Information**\n"
        "Access admission, registration, credit, retake, "
        "graduation and grading information.\n\n"
        "📅 **Academic Calendar**\n"
        "View the latest UIU academic calendars.\n\n"
        "📢 **Notices**\n"
        "Get the latest UIU notices.\n\n"
        "🔗 **Important Links**\n"
        "Quick access to official UIU resources.\n\n"
        "⚙️ **Settings**\n"
        "Manage your notification preferences.\n\n"
        "If you face any issue, use /start to restart the bot."
    )

    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
    )


async def show_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await help_command(
        update,
        context,
    )


async def about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    about_text = (
        "🤖 **UIU Student Assistant**\n\n"
        "A student-focused Telegram assistant for "
        "United International University.\n\n"
        "Version 2.0.0\n\n"
        "👨‍💻 **Developer:** @souravsahapartho\n\n"
        "*Disclaimer:* Fee and academic policy information "
        "may change. Please verify important decisions with "
        "official UIU sources."
    )

    await update.message.reply_text(
        about_text,
        parse_mode="Markdown",
    )


async def show_about(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await about(
        update,
        context,
    )


async def important_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = "🔗 **Important UIU Links**\n\n" "Select a link below to open it."

    await update.message.reply_text(
        text,
        reply_markup=get_links_keyboard(),
        parse_mode="Markdown",
    )


async def show_links(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await important_links(
        update,
        context,
    )


def grading_system_text():
    return (
        "📚 <b>UIU Grading System</b>\n\n"
        "<pre>"
        "Letter   Grade Point   Marks (%)\n"
        "──────────────────────────────\n"
        "A        4.00          90–100\n"
        "A−       3.67          86–89\n"
        "B+       3.33          82–85\n"
        "B        3.00          78–81\n"
        "B−       2.67          74–77\n"
        "C+       2.33          70–73\n"
        "C        2.00          66–69\n"
        "C−       1.67          62–65\n"
        "D+       1.33          58–61\n"
        "D        1.00          55–57\n"
        "F        0.00          0–54"
        "</pre>"
    )


async def academic_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    keyboard = [
        [
            InlineKeyboardButton(
                "🎓 Admission",
                url="https://www.uiu.ac.bd/admission/",
            ),
            InlineKeyboardButton(
                "📝 Registration",
                callback_data="acad_registration",
            ),
        ],
        [
            InlineKeyboardButton(
                "📊 Credit System",
                callback_data="acad_credit",
            ),
            InlineKeyboardButton(
                "🔄 Retake Rules",
                callback_data="acad_retake",
            ),
        ],
        [
            InlineKeyboardButton(
                "🎯 Graduation",
                url="https://convocation.uiu.ac.bd/",
            ),
            InlineKeyboardButton(
                "📚 Grading System",
                callback_data="acad_grading",
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Main Menu",
                callback_data="acad_back",
            ),
        ],
    ]

    await update.message.reply_text(
        "📚 **Academic Information**\n\n" "Select a topic:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def academic_info_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    await query.edit_message_text(
        "📚 **Academic Information**\n\n" "Select a topic:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎓 Admission",
                        url="https://www.uiu.ac.bd/admission/",
                    ),
                    InlineKeyboardButton(
                        "📝 Registration",
                        callback_data="acad_registration",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📊 Credit System",
                        callback_data="acad_credit",
                    ),
                    InlineKeyboardButton(
                        "🔄 Retake Rules",
                        callback_data="acad_retake",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🎯 Graduation",
                        url="https://convocation.uiu.ac.bd/",
                    ),
                    InlineKeyboardButton(
                        "📚 Grading System",
                        callback_data="acad_grading",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Main Menu",
                        callback_data="acad_back",
                    ),
                ],
            ]
        ),
        parse_mode="Markdown",
    )


async def academic_info_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    if text == "🎓 Admission":
        await update.message.reply_text(
            "🎓 **UIU Admission**\n\n"
            "Tap the button below to visit the official "
            "UIU admission page.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌐 Open Admission Page",
                            url="https://www.uiu.ac.bd/admission/",
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if text == "📝 Registration":
        await update.message.reply_text(
            "📝 **UIU Course Registration**\n\n"
            "Choose your preferred registration portal:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌐 UCam Cloud",
                            url="https://uiu.ucamcloud.com/",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔐 UCam — UIU",
                            url="https://ucam.uiu.ac.bd/Security/LogIn.aspx",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ],
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if text == "📊 Credit System":
        await update.message.reply_text(
            "🎓 **UIU Credit System**\n\n"
            "The **United International University (UIU)** "
            "follows a credit-hour-based academic system.\n\n"
            "📚 **Credit Hour**\n"
            "A credit hour represents the academic workload "
            "of a course.\n\n"
            "• **Theory Course:** Typically 3 credits\n"
            "• **Laboratory Course:** Typically 1–2 credits\n"
            "• **Project/Thesis:** Credits vary depending on "
            "the program and curriculum\n\n"
            "📊 **Degree Completion**\n"
            "Students must complete all required courses and "
            "the **total credits specified by their respective "
            "program curriculum** to fulfill the requirements "
            "for graduation.\n\n"
            "📌 **Important**\n"
            "Course credits, prerequisites, and total degree "
            "requirements may vary by **department, program, "
            "and curriculum revision**. Students should always "
            "refer to the latest official UIU curriculum for "
            "accurate information.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if text == "🔄 Retake Rules":
        await update.message.reply_text(
            "🔄 **UIU Retake Course Policy**\n\n"
            "Students at **United International University "
            "(UIU)** may retake a course according to the "
            "university's academic regulations.\n\n"
            "💰 **First-Time Retake Discount**\n"
            "Students receive a **50% tuition fee discount** "
            "when retaking a course **for the first time**.\n\n"
            "📌 **Key Points**\n"
            "• 🎓 The **first retake** is eligible for a "
            "50% discount for all students.\n"
            "• 🔄 The course must be registered again in a "
            "subsequent semester.\n"
            "• 📊 Retaking a course may affect the student's "
            "CGPA according to the applicable grading policy.\n"
            "• 📝 The retake attempt will be recorded in the "
            "student's academic record.\n"
            "• ⚠️ The applicable rules and fees should be "
            "verified with the latest UIU academic regulations "
            "before registration.\n\n"
            "💡 **Tip:** Check your course eligibility and "
            "retake fee before completing your registration.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if text == "🎯 Graduation":
        await update.message.reply_text(
            "🎯 **UIU Graduation & Convocation**\n\n"
            "Tap the button below to visit the official "
            "UIU Convocation portal.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌐 Open Convocation Portal",
                            url="https://convocation.uiu.ac.bd/",
                        )
                    ]
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if text == "📚 Grading System":
        await update.message.reply_text(
            grading_system_text(),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ]
                ]
            ),
            parse_mode="HTML",
        )
        return

    await update.message.reply_text("Information not available.")


async def academic_info_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "acad_back":
        await query.edit_message_text(
            "📚 **Academic Information**\n\n" "Select a topic:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎓 Admission",
                            url="https://www.uiu.ac.bd/admission/",
                        ),
                        InlineKeyboardButton(
                            "📝 Registration",
                            callback_data="acad_registration",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📊 Credit System",
                            callback_data="acad_credit",
                        ),
                        InlineKeyboardButton(
                            "🔄 Retake Rules",
                            callback_data="acad_retake",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "🎯 Graduation",
                            url="https://convocation.uiu.ac.bd/",
                        ),
                        InlineKeyboardButton(
                            "📚 Grading System",
                            callback_data="acad_grading",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Main Menu",
                            callback_data="acad_back",
                        ),
                    ],
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if query.data == "acad_back_info":
        await query.edit_message_text(
            "📚 **Academic Information**\n\n" "Select a topic:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🎓 Admission",
                            url="https://www.uiu.ac.bd/admission/",
                        ),
                        InlineKeyboardButton(
                            "📝 Registration",
                            callback_data="acad_registration",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "📊 Credit System",
                            callback_data="acad_credit",
                        ),
                        InlineKeyboardButton(
                            "🔄 Retake Rules",
                            callback_data="acad_retake",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "🎯 Graduation",
                            url="https://convocation.uiu.ac.bd/",
                        ),
                        InlineKeyboardButton(
                            "📚 Grading System",
                            callback_data="acad_grading",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Main Menu",
                            callback_data="acad_back",
                        ),
                    ],
                ]
            ),
            parse_mode="Markdown",
        )
        return

    if query.data == "acad_grading":
        await query.edit_message_text(
            grading_system_text(),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ]
                ]
            ),
            parse_mode="HTML",
        )
        return

    if query.data == "acad_registration":
        await query.edit_message_text(
            "📝 **UIU Course Registration**\n\n"
            "Choose your preferred registration portal:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🌐 UCam Cloud",
                            url="https://uiu.ucamcloud.com/",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔐 UCam — UIU",
                            url="https://ucam.uiu.ac.bd/Security/LogIn.aspx",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Academic Information",
                            callback_data="acad_back_info",
                        )
                    ],
                ]
            ),
            parse_mode="Markdown",
        )
        return

    information = {
        "acad_credit": (
            "🎓 **UIU Credit System**\n\n"
            "The **United International University (UIU)** "
            "follows a credit-hour-based academic system.\n\n"
            "📚 **Credit Hour**\n"
            "A credit hour represents the academic workload "
            "of a course.\n\n"
            "• **Theory Course:** Typically 3 credits\n"
            "• **Laboratory Course:** Typically 1–2 credits\n"
            "• **Project/Thesis:** Credits vary depending on "
            "the program and curriculum\n\n"
            "📊 **Degree Completion**\n"
            "Students must complete all required courses and "
            "the **total credits specified by their respective "
            "program curriculum** to fulfill the requirements "
            "for graduation.\n\n"
            "📌 **Important**\n"
            "Course credits, prerequisites, and total degree "
            "requirements may vary by **department, program, "
            "and curriculum revision**. Students should always "
            "refer to the latest official UIU curriculum for "
            "accurate information."
        ),
        "acad_retake": (
            "🔄 **UIU Retake Course Policy**\n\n"
            "Students at **United International University "
            "(UIU)** may retake a course according to the "
            "university's academic regulations.\n\n"
            "💰 **First-Time Retake Discount**\n"
            "Students receive a **50% tuition fee discount** "
            "when retaking a course **for the first time**.\n\n"
            "📌 **Key Points**\n"
            "• 🎓 The **first retake** is eligible for a "
            "50% discount for all students.\n"
            "• 🔄 The course must be registered again in a "
            "subsequent semester.\n"
            "• 📊 Retaking a course may affect the student's "
            "CGPA according to the applicable grading policy.\n"
            "• 📝 The retake attempt will be recorded in the "
            "student's academic record.\n"
            "• ⚠️ The applicable rules and fees should be "
            "verified with the latest UIU academic regulations "
            "before registration.\n\n"
            "💡 **Tip:** Check your course eligibility and "
            "retake fee before completing your registration."
        ),
    }

    text = information.get(
        query.data,
        "Information not available.",
    )

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Academic Information",
                        callback_data="acad_back_info",
                    )
                ]
            ]
        ),
        parse_mode="Markdown",
    )


async def notices(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text("⏳ Fetching latest notices from UIU website...")

    feed_url = "https://www.uiu.ac.bd/notice/feed/"

    try:
        feed = feedparser.parse(feed_url)

        if feed.entries:
            msg = "📢 **Latest UIU Notices:**\n\n"

            for entry in feed.entries[:5]:
                title = entry.get(
                    "title",
                    "Untitled Notice",
                )

                link = entry.get(
                    "link",
                    "",
                )

                msg += f"📌 **{title}**\n" f"🔗 [Read Full Notice]({link})\n\n"

            await update.message.reply_text(
                msg,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )

            return

    except Exception as error:
        logger.error(
            "Error fetching live notices: %s",
            error,
        )

    db_notices = get_recent_notices(5)

    if db_notices:
        msg = "📢 **Recent UIU Notices:**\n\n"

        for notice in db_notices:
            title = notice.get(
                "title",
                "Untitled Notice",
            )

            link = notice.get(
                "link",
                "",
            )

            msg += f"📌 **{title}**\n" f"🔗 [Read Full Notice]({link})\n\n"

        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )

    else:
        await update.message.reply_text(
            "📢 No notices available right now. " "Please check back later."
        )


async def settings_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_id = update.effective_user.id

    status = get_notification_status(user_id)

    status_text = "🟢 ON" if status else "🔴 OFF"

    keyboard = [
        [
            InlineKeyboardButton(
                f"🔔 Notifications: {status_text}",
                callback_data="toggle_alerts",
            )
        ]
    ]

    await update.message.reply_text(
        "⚙️ **Settings**\n\n" "Manage your notification preferences.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def settings_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "toggle_alerts":
        user_id = query.from_user.id

        new_status = toggle_notification(user_id)

        status_text = "🟢 ON" if new_status else "🔴 OFF"

        keyboard = [
            [
                InlineKeyboardButton(
                    f"🔔 Notifications: {status_text}",
                    callback_data="toggle_alerts",
                )
            ]
        ]

        await query.edit_message_text(
            "⚙️ **Settings**\n\n" f"🔔 Notifications: **{status_text}**",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


async def handle_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "❌ Action cancelled.",
        reply_markup=get_main_menu(),
    )


async def show_not_implemented(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🚧 This feature is currently being updated.",
        reply_markup=get_main_menu(),
    )
