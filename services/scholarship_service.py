import math
import random
import statistics

PROGRAM_CREDIT_REQUIREMENTS = {
    "BBA": 9,
    "BBA in AIS": 9,
    "BSECO": 9,
    "BSCSE": 9,
    "BSEEE": 9,
    "BSDS": 9,
    "B.Sc. in CE": 9,
    "BSSEDS": 9,
    "BSSMSJ": 9,
    "BA in English": 9,
    "B.Pharm": 14,
    "BSBGE": 9,
}

GRADUATE_PROGRAMS = {
    "Graduate",
    "MBA",
    "EMBA",
    "MS",
    "MSc",
    "Masters",
}

MINIMUM_GPA = 3.50

SIMULATIONS = 10000


def normalize_program(program):
    value = str(program).strip()

    if value in PROGRAM_CREDIT_REQUIREMENTS:
        return value

    if value in GRADUATE_PROGRAMS:
        return value

    return value


def get_minimum_credits(program):
    program = normalize_program(program)

    if program in PROGRAM_CREDIT_REQUIREMENTS:
        return PROGRAM_CREDIT_REQUIREMENTS[program]

    if program in GRADUATE_PROGRAMS:
        return 6

    return 9


def validate_eligibility(
    gpa,
    program,
    qualifying_credits,
):
    program = normalize_program(program)

    try:
        gpa = float(gpa)
        qualifying_credits = float(qualifying_credits)
    except (TypeError, ValueError):
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    if gpa < MINIMUM_GPA:
        return {
            "eligible": False,
            "reason": "gpa",
            "minimum_gpa": MINIMUM_GPA,
            "gpa": gpa,
        }

    minimum_credits = get_minimum_credits(program)

    if qualifying_credits < minimum_credits:
        return {
            "eligible": False,
            "reason": "credits",
            "minimum_credits": minimum_credits,
            "qualifying_credits": qualifying_credits,
        }

    return {
        "eligible": True,
        "minimum_credits": minimum_credits,
        "qualifying_credits": qualifying_credits,
    }


def estimate_higher_students_from_gpa(
    gpa,
    total_students,
):
    gpa = max(
        3.50,
        min(4.00, float(gpa)),
    )

    normalized = (gpa - 3.50) / 0.50

    percentile_top = 0.10 * (normalized**1.35)

    estimated_top_fraction = max(
        0.01,
        min(0.10, percentile_top),
    )

    estimated_higher = total_students * estimated_top_fraction

    return max(
        0,
        min(
            total_students - 1,
            estimated_higher,
        ),
    )


def estimate_higher_student_range(
    gpa,
    total_students,
    higher_students=None,
):
    if higher_students is not None:
        higher_students = max(
            0,
            min(
                total_students - 1,
                int(higher_students),
            ),
        )

        spread = max(
            2,
            int(round(higher_students * 0.25)),
        )

        low = max(
            0,
            higher_students - spread,
        )

        high = min(
            total_students - 1,
            higher_students + spread,
        )

        return low, high, True

    estimated = estimate_higher_students_from_gpa(
        gpa,
        total_students,
    )

    spread = max(
        5,
        int(round(total_students * 0.04)),
    )

    low = max(
        0,
        int(round(estimated - spread)),
    )

    high = min(
        total_students - 1,
        int(round(estimated + spread)),
    )

    return low, high, False


def scholarship_bracket(
    position,
    total_students,
):
    top_2 = max(
        1,
        math.ceil(total_students * 0.02),
    )

    top_6 = max(
        top_2,
        math.ceil(total_students * 0.06),
    )

    top_10 = max(
        top_6,
        math.ceil(total_students * 0.10),
    )

    if position <= top_2:
        return "100%"

    if position <= top_6:
        return "50%"

    if position <= top_10:
        return "25%"

    return "No Scholarship"


def run_monte_carlo_simulation(
    gpa,
    total_students,
    higher_students=None,
    simulations=SIMULATIONS,
):
    low, high, user_estimate = estimate_higher_student_range(
        gpa,
        total_students,
        higher_students,
    )

    outcomes = {
        "100%": 0,
        "50%": 0,
        "25%": 0,
        "No Scholarship": 0,
    }

    positions = []

    for _ in range(simulations):
        if user_estimate:
            estimated_higher = random.triangular(
                low,
                high,
                (low + high) / 2,
            )
        else:
            estimated_higher = random.triangular(
                low,
                high,
                (low + high) / 2,
            )

        estimated_higher = max(
            0,
            min(
                total_students - 1,
                int(round(estimated_higher)),
            ),
        )

        position = estimated_higher + 1

        if position > total_students:
            position = total_students

        positions.append(position)

        bracket = scholarship_bracket(
            position,
            total_students,
        )

        outcomes[bracket] += 1

    probabilities = {key: (value / simulations) for key, value in outcomes.items()}

    return {
        "probabilities": probabilities,
        "positions": positions,
        "higher_range": (
            low,
            high,
        ),
        "used_user_estimate": user_estimate,
        "simulations": simulations,
    }


def calculate_confidence(
    total_students,
    higher_students,
    used_user_estimate,
):
    score = 0

    if total_students >= 100:
        score += 1

    if total_students >= 300:
        score += 1

    if higher_students is not None:
        score += 2

    if used_user_estimate:
        score += 1

    if score >= 4:
        return "High"

    if score >= 2:
        return "Medium"

    return "Low"


def top_range_from_positions(
    positions,
    total_students,
):
    percentages = [(position / total_students) * 100 for position in positions]

    low = min(percentages)

    high = max(percentages)

    low = max(
        0.1,
        low,
    )

    return (
        low,
        high,
    )


def round_probability(
    probability,
):
    percentage = probability * 100

    if percentage < 1:
        return "<1%"

    rounded = int(round(percentage / 5) * 5)

    rounded = max(
        5,
        min(
            100,
            rounded,
        ),
    )

    return f"{rounded}%"


def most_likely_outcome(
    probabilities,
):
    ordered = [
        "100%",
        "50%",
        "25%",
        "No Scholarship",
    ]

    return max(
        ordered,
        key=lambda key: probabilities.get(
            key,
            0,
        ),
    )


def generate_estimate(
    gpa,
    program,
    total_students,
    qualifying_credits,
    higher_students=None,
):
    eligibility = validate_eligibility(
        gpa,
        program,
        qualifying_credits,
    )

    if not eligibility["eligible"]:
        return {
            "eligible": False,
            "eligibility": eligibility,
        }

    total_students = int(total_students)

    result = run_monte_carlo_simulation(
        gpa=float(gpa),
        total_students=total_students,
        higher_students=higher_students,
        simulations=SIMULATIONS,
    )

    probabilities = result["probabilities"]

    confidence = calculate_confidence(
        total_students,
        higher_students,
        result["used_user_estimate"],
    )

    position_low, position_high = top_range_from_positions(
        result["positions"],
        total_students,
    )

    most_likely = most_likely_outcome(probabilities)

    return {
        "eligible": True,
        "gpa": float(gpa),
        "program": program,
        "total_students": total_students,
        "qualifying_credits": float(qualifying_credits),
        "minimum_credits": eligibility["minimum_credits"],
        "higher_students": higher_students,
        "higher_range": result["higher_range"],
        "probabilities": probabilities,
        "display_probabilities": {
            key: round_probability(value) for key, value in probabilities.items()
        },
        "confidence": confidence,
        "most_likely": most_likely,
        "position_top_range": (
            position_low,
            position_high,
        ),
        "simulations": SIMULATIONS,
    }


def format_top_range(
    low,
    high,
):
    low = round(low)
    high = round(high)

    if low == high:
        return f"Top {low}%"

    return f"Top {low}–{high}%"


def generate_result_text(
    result,
):
    gpa = result["gpa"]

    program = result["program"]

    total_students = result["total_students"]

    credits = result["qualifying_credits"]

    minimum_credits = result["minimum_credits"]

    probabilities = result["display_probabilities"]

    low, high = result["position_top_range"]

    most_likely = result["most_likely"]

    confidence = result["confidence"]

    top_range = format_top_range(
        low,
        high,
    )

    return (
        "━━━━━━━━━━━━━━━━━━\n"
        "🎓 <b>Scholarship Estimate</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Previous GPA:</b> {gpa:.2f}\n"
        f"<b>Program:</b> {program}\n"
        f"<b>Program Size:</b> ~{total_students} students\n"
        f"<b>Qualifying Credits:</b> {credits:g}\n"
        f"<b>Minimum Required:</b> {minimum_credits:g}\n\n"
        f"📊 <b>Estimated Position:</b> {top_range}\n\n"
        "🏆 <b>Estimated Scholarship Chances</b>\n\n"
        f"🥇 100% → <b>{probabilities['100%']}</b>\n"
        f"🥈 50% → <b>{probabilities['50%']}</b>\n"
        f"🥉 25% → <b>{probabilities['25%']}</b>\n"
        f"❌ No Scholarship → <b>{probabilities['No Scholarship']}</b>\n\n"
        f"🎯 <b>Most Likely Outcome:</b> "
        f"{most_likely} Scholarship\n\n"
        f"📈 <b>Confidence:</b> {confidence}\n\n"
        "⚠️ <b>Important:</b> This estimator provides "
        "an approximate statistical prediction based on "
        "the information available. It is not an official "
        "UIU ranking or scholarship decision. Final scholarship "
        "decisions are determined by UIU.\n\n"
        "📌 Scholarship is subject to the applicable credit "
        "limit and excludes Thesis, Project, Internship, "
        "Retake and Repeat courses."
    )


def generate_ineligible_text(
    eligibility,
):
    reason = eligibility["reason"]

    if reason == "gpa":
        return (
            "❌ <b>Not Eligible for Merit Scholarship</b>\n\n"
            f"Your previous trimester/semester GPA is "
            f"<b>{eligibility['gpa']:.2f}</b>, which is below "
            f"the minimum required GPA of "
            f"<b>{eligibility['minimum_gpa']:.2f}</b>.\n\n"
            "The top 10% ranking does not override the "
            "minimum GPA requirement."
        )

    if reason == "credits":
        return (
            "❌ <b>Minimum Credit Requirement Not Met</b>\n\n"
            f"Your qualifying credits: "
            f"<b>{eligibility['qualifying_credits']:g}</b>\n"
            f"Minimum required: "
            f"<b>{eligibility['minimum_credits']:g}</b>\n\n"
            "Based on the provided information, you do not "
            "meet the minimum credit requirement for the "
            "scholarship estimator."
        )

    return (
        "⚠️ <b>Invalid Information</b>\n\n"
        "Please check your GPA, program and credit information "
        "and try again."
    )


def scholarship_rules_text():
    return (
        "🎓 <b>UIU Merit Scholarship Rules</b>\n\n"
        "🏆 <b>Scholarship Brackets</b>\n\n"
        "🥇 Top 2% → <b>100%</b>\n"
        "🥈 Next 4% → <b>50%</b>\n"
        "🥉 Next 4% → <b>25%</b>\n\n"
        "📊 Approximately the top 10% may receive a merit "
        "scholarship, subject to eligibility requirements.\n\n"
        "📈 <b>Minimum GPA:</b> 3.50 in the just-previous "
        "trimester/semester.\n\n"
        "📚 <b>Minimum Qualifying Credits</b>\n\n"
        "BBA, BBA in AIS, BSECO, BSCSE, BSEEE, BSDS, "
        "B.Sc. in CE, BSSEDS, BSSMSJ, BA in English, "
        "BSBGE → 9 credits\n\n"
        "B.Pharm → 14 credits\n\n"
        "Graduate → 6 credits\n\n"
        "🚫 <b>Excluded Courses</b>\n"
        "Thesis, Project, Internship, Retake and Repeat "
        "courses are excluded from merit scholarship coverage.\n\n"
        "⚠️ Scholarship eligibility and ranking depend on "
        "official UIU regulations and merit assessment."
    )
