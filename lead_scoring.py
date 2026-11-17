
def calculate_lead_score(analysis):

    # Base score
    score = 30

    # Urgency bonus
    if analysis["urgency"] == "Urgent":
        score += 30

    # Budget bonus
    if analysis["budget"] != "Not mentioned":
        score += 20

    # Business category bonus
    if analysis["category"] in [
        "AI Automation",
        "AI Chatbot",
        "Website Development",
        "ERP / Software Solution",
        "ERP Software"
    ]:
        score += 20

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
        "priority": priority
    }
