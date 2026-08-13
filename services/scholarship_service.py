import math
import random

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
    if program is None:
        return ""

    return str(program).strip()


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
    try:
        gpa = float(gpa)
        qualifying_credits = float(qualifying_credits)
    except (TypeError, ValueError):
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    if not math.isfinite(gpa):
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    if not math.isfinite(qualifying_credits):
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    if not 0 <= gpa <= 4:
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    if qualifying_credits <= 0:
        return {
            "eligible": False,
            "reason": "invalid_input",
        }

    minimum_credits = get_minimum_credits(program)

    if gpa < MINIMUM_GPA:
        return {
            "eligible": False,
            "reason": "gpa",
            "minimum_gpa": MINIMUM_GPA,
            "gpa": gpa,
            "minimum_credits": minimum_credits,
            "qualifying_credits": qualifying_credits,
        }

    if qualifying_credits < minimum_credits:
        return {
            "eligible": False,
            "reason": "credits",
            "minimum_credits": minimum_credits,
            "qualifying_credits": qualifying_credits,
            "gpa": gpa,
        }

    return {
        "eligible": True,
        "minimum_credits": minimum_credits,
        "qualifying_credits": qualifying_credits,
        "gpa": gpa,
    }


def estimate_higher_students_from_gpa(
    gpa,
    total_students,
):
    gpa = float(gpa)

    total_students = int(total_students)

    gpa = max(
        3.50,
        min(
            4.00,
            gpa,
        ),
    )

    total_students = max(
        10,
        total_students,
    )

    normalized = (gpa - 3.50) / 0.50

    percentile_top = 0.10 * (normalized**1.35)

    estimated_top_fraction = max(
        0.01,
        min(
            0.10,
            percentile_top,
        ),
    )

    estimated_higher = total_students * estimated_top_fraction

    estimated_higher = int(round(estimated_higher))

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
    total_students = int(total_students)

    if total_students < 2:
        return (
            0,
            0,
            False,
        )

    if higher_students is not None:
        higher_students = int(higher_students)

        higher_students = max(
            0,
            min(
                total_students - 1,
                higher_students,
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

        return (
            low,
            high,
            True,
        )

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

    return (
        low,
        high,
        False,
    )


def scholarship_bracket(
    position,
    total_students,
):
    position = max(
        1,
        int(position),
    )

    total_students = max(
        1,
        int(total_students),
    )

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
    total_students = int(total_students)

    simulations = max(
        1000,
        int(simulations),
    )

    low, high, user_estimate = estimate_higher_student_range(
        gpa,
        total_students,
        higher_students,
    )

    low = float(low)
    high = float(high)

    if high < low:
        high = low

    mode = (low + high) / 2

    outcomes = {
        "100%": 0,
        "50%": 0,
        "25%": 0,
        "No Scholarship": 0,
    }

    positions = []

    for _ in range(simulations):
        if low == high:
            estimated_higher = low
        else:
            estimated_higher = random.triangular(
                low,
                high,
                mode,
            )

        estimated_higher = int(round(estimated_higher))

        estimated_higher = max(
            0,
            min(
                total_students - 1,
                estimated_higher,
            ),
        )

        position = estimated_higher + 1

        position = max(
            1,
            min(
                total_students,
                position,
            ),
        )

        positions.append(position)

        bracket = scholarship_bracket(
            position,
            total_students,
        )

        outcomes[bracket] += 1

    probabilities = {key: value / simulations for key, value in outcomes.items()}

    return {
        "probabilities": probabilities,
        "positions": positions,
        "higher_range": (
            int(low),
            int(high),
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
    if not positions:
        return (
            10.0,
            10.0,
        )

    total_students = max(
        1,
        int(total_students),
    )

    percentages = [(position / total_students) * 100 for position in positions]

    low = min(percentages)

    high = max(percentages)

    low = max(
        0.1,
        low,
    )

    high = max(
        low,
        high,
    )

    return (
        low,
        high,
    )


def round_probability(
    probability,
):
    percentage = float(probability) * 100

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

    try:
        total_students = int(total_students)

        if total_students < 10:
            return {
                "eligible": False,
                "eligibility": {
                    "reason": "invalid_input",
                },
            }

        if higher_students is not None:
            higher_students = int(higher_students)

            if higher_students < 0 or higher_students >= total_students:
                return {
                    "eligible": False,
                    "eligibility": {
                        "reason": "higher_students",
                        "total_students": total_students,
                    },
                }

        simulation = run_monte_carlo_simulation(
            gpa=float(gpa),
            total_students=total_students,
            higher_students=higher_students,
            simulations=SIMULATIONS,
        )

        probabilities = simulation["probabilities"]

        confidence = calculate_confidence(
            total_students,
            higher_students,
            simulation["used_user_estimate"],
        )

        position_low, position_high = top_range_from_positions(
            simulation["positions"],
            total_students,
        )

        most_likely = most_likely_outcome(probabilities)

        return {
            "eligible": True,
            "gpa": float(gpa),
            "program": normalize_program(program),
            "total_students": total_students,
            "qualifying_credits": float(qualifying_credits),
            "minimum_credits": eligibility["minimum_credits"],
            "higher_students": higher_students,
            "higher_range": simulation["higher_range"],
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
            "simulations": simulation["simulations"],
            "estimate_source": (
                "user_estimate"
                if higher_students is not None
                else "statistical_estimate"
            ),
            "is_exact": False,
        }

    except Exception:
        return {
            "eligible": False,
            "eligibility": {
                "reason": "calculation_error",
            },
        }


def format_top_range(
    low,
    high,
):
    low = round(
        float(low),
        1,
    )

    high = round(
        float(high),
        1,
    )

    if low == high:
        return f"Top {low:g}%"

    return f"Top {low:g}–{high:g}%"


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

    source = result.get(
        "estimate_source",
        "statistical_estimate",
    )

    if source == "user_estimate":
        basis_text = (
            "Your estimated number of higher-GPA " "students was used as an input."
        )
    else:
        basis_text = (
            "The number of higher-GPA students was "
            "estimated statistically from the available "
            "information."
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
        f"📊 <b>Estimated Position:</b> "
        f"{top_range}\n\n"
        "🏆 <b>Estimated Scholarship Chances</b>\n\n"
        f"🥇 100% → <b>{probabilities['100%']}</b>\n"
        f"🥈 50% → <b>{probabilities['50%']}</b>\n"
        f"🥉 25% → <b>{probabilities['25%']}</b>\n"
        f"❌ No Scholarship → "
        f"<b>{probabilities['No Scholarship']}</b>\n\n"
        f"🎯 <b>Most Likely Outcome:</b> "
        f"{most_likely}\n\n"
        f"📈 <b>Confidence:</b> {confidence}\n\n"
        f"🧮 <b>Estimation Basis:</b>\n"
        f"{basis_text}\n\n"
        "⚠️ <b>Important:</b> This is only an "
        "<b>approximate statistical estimate</b>, not an "
        "exact ranking or official UIU scholarship decision.\n\n"
        "Final scholarship decisions are determined by UIU "
        "according to its applicable rules and actual student "
        "performance.\n\n"
        "📌 Scholarship is subject to the applicable credit "
        "limit and excludes Thesis, Project, Internship, "
        "Retake and Repeat courses."
    )


def generate_ineligible_text(
    eligibility,
):
    reason = eligibility.get(
        "reason",
        "invalid_input",
    )

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
            "meet the minimum credit requirement."
        )

    if reason == "higher_students":
        return (
            "⚠️ <b>Invalid Higher-GPA Estimate</b>\n\n"
            "The estimated number of students with a higher "
            "GPA must be smaller than the total program size."
        )

    if reason == "calculation_error":
        return (
            "⚠️ <b>Unable to Complete Estimate</b>\n\n"
            "The statistical calculation could not be completed "
            "right now. Please try again."
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
        "⚠️ The estimator is not an official UIU ranking "
        "or scholarship decision."
    )
