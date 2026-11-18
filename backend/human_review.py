COMPLAINT_WORDS = [
    "unhappy", "complaint", "not satisfied", "dissatisfied",
    "disappointed", "refund", "angry", "bad service",
    "poor service", "worst", "call me",
]

PRICING_WORDS = [
    "price", "pricing", "cost", "quote", "quotation",
    "how much", "rate card", "charges",
]

PARTNERSHIP_WORDS = [
    "partner", "partnership", "collaborate", "collaboration",
    "joint venture",
]

SENSITIVE_WORDS = [
    "legal", "lawyer", "court", "police", "fraud", "scam",
]


def check_human_review(message, analysis, lead_score):
    """Decide whether a human must review this enquiry, and explain why."""
    text = message.lower()
    reasons = []

    if any(word in text for word in COMPLAINT_WORDS):
        reasons.append("Possible complaint or unhappy customer")

    if any(word in text for word in PRICING_WORDS):
        reasons.append("Customer asked about pricing - prices must not be invented")

    if any(word in text for word in PARTNERSHIP_WORDS):
        reasons.append("Partnership enquiry - needs a business decision")

    if any(word in text for word in SENSITIVE_WORDS):
        reasons.append("Sensitive topic - needs human handling")

    if analysis["category"] == "General Enquiry":
        reasons.append("Enquiry is unclear or general")

    if lead_score["priority"] == "High":
        reasons.append("High priority lead - important opportunity")

    return {
        "needs_human_review": len(reasons) > 0,
        "reasons": reasons
    }