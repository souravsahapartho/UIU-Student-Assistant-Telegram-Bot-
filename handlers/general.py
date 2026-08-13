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
    get_academic_info_menu,
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
        f"👋 Welcome to **UIU Smart Assistant**, {user.first_name}!\n\n"
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
        "Check scholarship-related calculations.\n\n"
        "📚 **Academic Information**\n"
        "Access important academic information.\n\n"
        "📢 **Notices**\n"
        "Get the latest UIU notices.\n\n"
        "🔗 **Important Links**\n"
        "Quick access to official UIU resources.\n\n"
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
        "🤖 **UIU Smart Assistant**\n\n"
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


async def academic_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "📚 **Academic Information**\n\n" "Select a topic:",
        reply_markup=get_academic_info_menu(),
        parse_mode="Markdown",
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
        "</pre>\n\n"
        "📌 This grading scale is used for CGPA calculation."
    )


async def academic_info_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query

    await query.answer()

    if query.data == "acad_grading":
        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Academic Information",
                    callback_data="acad_back_info",
                )
            ]
        ]

        await query.edit_message_text(
            grading_system_text(),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
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

    if query.data == "acad_back":
        await query.edit_message_text("Use /start to return to the main menu.")
        return

    information = {
        "acad_registration": (
            "📝 **Registration**\n\n"
            "Course registration information and deadlines "
            "should be verified through UCAM and official UIU announcements."
        ),
        "acad_credit": (
            "📊 **Credit System**\n\n"
            "Credit requirements depend on the academic program. "
            "Check your department's official curriculum."
        ),
        "acad_retake": (
            "🔄 **Retake Rules**\n\n"
            "Retake and improvement policies may change. "
            "Please verify the current policy through official UIU sources."
        ),
    }

    text = information.get(
        query.data,
        "Information not available.",
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ Academic Information",
                callback_data="acad_back_info",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
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

    except Exception as e:
        logger.error(
            "Error fetching live notices: %s",
            e,
        )

    db_notices = get_recent_notices(5)

    if db_notices:
        msg = "📢 **Recent UIU Notices:**\n\n"

        for notice in db_notices:
            msg += (
                f"📌 **{notice['title']}**\n"
                f"🔗 [Read Full Notice]({notice['link']})\n\n"
            )

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
        ],
        [
            InlineKeyboardButton(
                "⬅️ Main Menu",
                callback_data="settings_back",
            )
        ],
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
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Main Menu",
                    callback_data="settings_back",
                )
            ],
        ]

        await query.edit_message_text(
            "⚙️ **Settings**\n\n" f"🔔 Notifications are now {status_text}.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif query.data == "settings_back":
        await query.edit_message_text("Use /start to return to the main menu.")


async def handle_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "❌ Cancelled.",
        reply_markup=get_main_menu(),
    )


async def academic_info_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "⬅️ Main Menu",
        reply_markup=get_main_menu(),
    )


async def academic_admission(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🎓 <b>Admission</b>\n\n" "Open the official UIU admission page:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎓 Open Admission",
                        url="https://www.uiu.ac.bd/admission/",
                    )
                ]
            ]
        ),
        parse_mode="HTML",
    )


async def academic_graduation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🎯 <b>Graduation</b>\n\n" "Open the official UIU Convocation page:",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎯 Open Graduation",
                        url="https://convocation.uiu.ac.bd/",
                    )
                ]
            ]
        ),
        parse_mode="HTML",
    )


async def academic_grading(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        grading_system_text(),
        parse_mode="HTML",
        reply_markup=get_academic_info_menu(),
    )


async def academic_registration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "📝 <b>UIU Course Registration</b>\n\n"
        "Choose your preferred registration portal:\n\n"
        "🌐 <b>UCam Cloud</b>\n"
        "https://uiu.ucamcloud.com/\n\n"
        "🔐 <b>UCam — UIU</b>\n"
        "https://ucam.uiu.ac.bd/Security/LogIn.aspx\n\n"
        "📌 Use your UIU credentials to log in and access "
        "course registration and related academic services."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=get_academic_info_menu(),
    )


async def academic_credit(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "🎓 <b>UIU Credit System</b>\n\n"
        "The <b>United International University (UIU)</b> "
        "follows a credit-hour-based academic system.\n\n"
        "📚 <b>Credit Hour</b>\n\n"
        "• <b>Theory Course:</b>\n"
        "  Typically 3 credits\n\n"
        "• <b>Laboratory Course:</b>\n"
        "  Typically 1–2 credits\n\n"
        "• <b>Project/Thesis:</b>\n"
        "  Credits vary depending on the program and curriculum\n\n"
        "📊 <b>Degree Completion</b>\n\n"
        "Students must complete all required courses and the "
        "<b>total credits specified by their respective program "
        "curriculum</b> to fulfill the requirements for graduation.\n\n"
        "📌 <b>Important</b>\n\n"
        "Course credits, prerequisites, and total degree "
        "requirements may vary by <b>department, program, and "
        "curriculum revision</b>.\n\n"
        "Students should always refer to the latest official "
        "UIU curriculum for accurate information."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=get_academic_info_menu(),
    )


async def academic_retake(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "🔄 <b>UIU Retake Course Policy</b>\n\n"
        "Students at <b>United International University (UIU)</b> "
        "may retake a course according to the university's "
        "academic regulations.\n\n"
        "💰 <b>First-Time Retake Discount</b>\n\n"
        "Students receive a <b>50% tuition fee discount</b> "
        "when retaking a course <b>for the first time</b>.\n\n"
        "📌 <b>Key Points</b>\n\n"
        "• 🎓 The <b>first retake</b> is eligible for a "
        "<b>50% discount</b> for all students.\n\n"
        "• 🔄 The course must be registered again in a "
        "subsequent semester.\n\n"
        "• 📊 Retaking a course may affect the student's "
        "<b>CGPA</b> according to the applicable grading policy.\n\n"
        "• 📝 The retake attempt will be recorded in the "
        "student's academic record.\n\n"
        "• ⚠️ The applicable rules and fees should be verified "
        "with the latest UIU academic regulations before registration.\n\n"
        "💡 <b>Tip:</b> Check your course eligibility and "
        "retake fee before completing your registration."
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=get_academic_info_menu(),
    )


async def academic_info_menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    if text == "🎓 Admission":
        await academic_admission(
            update,
            context,
        )
        return

    if text == "📝 Registration":
        await academic_registration(
            update,
            context,
        )
        return

    if text == "📊 Credit System":
        await academic_credit(
            update,
            context,
        )
        return

    if text == "🔄 Retake Rules":
        await academic_retake(
            update,
            context,
        )
        return

    if text == "🎯 Graduation":
        await academic_graduation(
            update,
            context,
        )
        return

    if text == "📚 Grading System":
        await academic_grading(
            update,
            context,
        )
        return


async def show_not_implemented(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text("🚧 This feature is currently being updated.")
