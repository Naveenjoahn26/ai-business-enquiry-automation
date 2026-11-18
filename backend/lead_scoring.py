# Categories that are real business opportunities
BUSINESS_CATEGORIES = [
    "Business Consulting",
    "AI Automation",
    "Website & App Development",
    "Operational Systems / ERP",
    "Branding & Marketing",
]


def calculate_lead_score(analysis):

    # Base score
    score = 30
    reasons = ["Base score: +30"]

    # Urgency bonus
    if analysis["urgency"] == "Urgent":
        score += 30
        reasons.append("Customer showed urgency: +30")

    # Budget bonus
    if analysis["budget"] != "Not mentioned":
        score += 20
        reasons.append("Budget was mentioned: +20")

    # Business category bonus
    if analysis["category"] in BUSINESS_CATEGORIES:
        score += 20
        reasons.append(f"Relevant business category ({analysis['category']}): +20")

    # Maximum score should be 100
    score = min(score, 100)

    # Priority classification
    if score >= 70:
        priority = "High"
    elif score >= 40:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": score,
        "priority": priority,
        "reasons": reasons
    }