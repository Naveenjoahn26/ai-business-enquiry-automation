import json
import re
import urllib.request

CATEGORIES = [
    "Business Consulting",
    "AI Automation",
    "Website & App Development",
    "Operational Systems / ERP",
    "Branding & Marketing",
    "General Enquiry",
    "Job / Internship",
]

UNIT_PATTERN = r"(?P<unit>lakhs?|lacs?|crores?|k\b)?"
NUMBER_PATTERN = r"(?P<num>\d[\d,]*(?:\.\d+)?)"

# Budget patterns, checked in this order
BUDGET_PATTERNS = [
    # Rs 50000, INR 2 lakh, ₹2 lakh
    re.compile(
        r"(?<![a-z])(?P<cur>₹|rs\.?|inr)\s*" + NUMBER_PATTERN + r"\s*" + UNIT_PATTERN,
        re.IGNORECASE,
    ),
    # budget is 50000, budget of 2 lakh
    re.compile(
        r"budget\s*(?:is|of|:|around|about)?\s*(?P<cur>₹|rs\.?|inr)?\s*"
        + NUMBER_PATTERN + r"\s*" + UNIT_PATTERN,
        re.IGNORECASE,
    ),
    # 2 lakh, 3 crore
    re.compile(
        NUMBER_PATTERN + r"\s*(?P<unit>lakhs?|lacs?|crores?)",
        re.IGNORECASE,
    ),
]

TIMELINE_PATTERN = re.compile(
    r"(this week|next week|this month|next month|today|tomorrow|tonight|immediately"
    r"|within\s+\d+\s*(?:days?|weeks?|months?)"
    r"|in\s+\d+\s*(?:days?|weeks?|months?)"
    r"|\d+\s*(?:days?|weeks?|months?))",
    re.IGNORECASE,
)


def _extract_budget_from_message(message):
    """Backup: find a budget written in the customer's message using rules."""
    for pattern in BUDGET_PATTERNS:
        match = pattern.search(message)
        if not match:
            continue

        groups = match.groupdict()
        number = groups.get("num")
        if not number:
            continue

        unit = (groups.get("unit") or "").strip()
        currency = groups.get("cur")

        text = number
        if unit:
            text = f"{number} {unit}"
        if currency:
            text = f"₹{text}"
        return text

    return None


def _extract_timeline_from_message(message):
    """Backup: find a timeline written in the customer's message using rules."""
    match = TIMELINE_PATTERN.search(message)
    if match:
        return match.group(0).strip()
    return None


def _budget_is_in_message(budget, message):
    """Return True only if the budget number really appears in the customer's message."""
    budget_digits = re.sub(r"\D", "", str(budget))
    if not budget_digits:
        return False

    message_lower = message.lower()
    found_numbers = re.findall(r"\d[\d,\.]*", message_lower)

    allowed = set()
    for number_text in found_numbers:
        cleaned = number_text.replace(",", "")
        try:
            value = float(cleaned)
        except ValueError:
            continue

        allowed.add(str(int(value)))
        if "lakh" in message_lower or "lac" in message_lower:
            allowed.add(str(int(value * 100000)))
        if "crore" in message_lower:
            allowed.add(str(int(value * 10000000)))
        if re.search(r"\d\s*k\b", message_lower):
            allowed.add(str(int(value * 1000)))

    return budget_digits in allowed


def _timeline_is_in_message(message):
    """Return True only if the message contains some time-related word."""
    time_words = [
        "day", "week", "month", "year", "today", "tomorrow",
        "tonight", "immediately", "quarter", "hour"
    ]
    message_lower = message.lower()
    return any(word in message_lower for word in time_words)


def _is_job_or_internship(message):
    keywords = [
        "internship", "intern ", "job", "hiring", "vacancy",
        "career", "college project", "student", "placement"
    ]
    message_lower = message.lower()
    return any(word in message_lower for word in keywords)


def _category_from_keywords(message):
    """Rule-based category decision based only on the customer's message."""
    text = message.lower()

    if any(w in text for w in ["erp", "inventory", "dispatch", "stock", "operations"]):
        return "Operational Systems / ERP"
    if any(w in text for w in ["website", "web site", "mobile app", "app development", "application"]):
        return "Website & App Development"
    if re.search(r"\bai\b", text) or any(
        w in text for w in ["automat", "chatbot", "whatsapp", "assistant"]
    ):
        return "AI Automation"
    if any(w in text for w in ["marketing", "branding", "brand", "seo", "social media"]):
        return "Branding & Marketing"
    if any(w in text for w in ["consult", "strategy", "business intelligence", "dashboard", "reporting"]):
        return "Business Consulting"
    return "General Enquiry"


def _final_category(message):
    """The small AI model is not reliable for categories, so rules decide."""
    if _is_job_or_internship(message):
        return "Job / Internship"
    return _category_from_keywords(message)


def _meaningful_words(text):
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return set(words)


def _safe_requirement(ai_requirement, message):
    """Use the AI requirement only if it really relates to the customer's message."""
    ai_words = _meaningful_words(ai_requirement)
    message_words = _meaningful_words(message)

    overlap = ai_words & message_words
    if len(overlap) >= 2:
        return ai_requirement

    # AI text does not match the message, so use the customer's own words
    cleaned = " ".join(message.split())
    if len(cleaned) > 200:
        cleaned = cleaned[:200].rstrip() + "..."
    return cleaned


def classify_enquiry(message):

    prompt = f"""
You are a business enquiry analyst.

Read the customer's message:
{message}

Extract information ONLY from the customer's message above.

Return JSON with exactly these five fields:
- "category": the service area of the enquiry
- "requirement": one short sentence using the customer's own words
- "budget": the budget exactly as the customer wrote it, or "Not mentioned"
- "timeline": the timeline exactly as the customer wrote it, or "Not mentioned"
- "urgency": "Urgent" only if the customer asks for urgency, otherwise "Normal"

Rules:
- Use only facts that are in the customer's message.
- Never invent a budget, timeline, service or requirement.
- If the customer did not say it, write "Not mentioned".
"""

    payload = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": "Extract business enquiry details accurately from the customer's message only. Never invent information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    try:
        request = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))

        result = json.loads(data["message"]["content"])

        required_fields = [
            "category", "requirement", "budget",
            "timeline", "urgency"
        ]

        if not all(field in result for field in required_fields):
            raise ValueError("AI response is missing required fields")

        # Make sure every value is plain text
        for field in required_fields:
            result[field] = str(result[field]).strip()

        # Category is decided by rules (AI category is not trusted)
        result["category"] = _final_category(message)

        # Requirement must relate to the customer's message
        result["requirement"] = _safe_requirement(result["requirement"], message)

        # Verify urgency using the original customer message
        message_lower = message.lower()

        urgent_keywords = [
            "urgent",
            "urgently",
            "asap",
            "immediately",
            "emergency",
            "high priority",
            "as soon as possible"
        ]

        if any(word in message_lower for word in urgent_keywords):
            result["urgency"] = "Urgent"
        else:
            result["urgency"] = "Normal"

        # Budget: remove invented values, then add a missed one using rules
        if not _budget_is_in_message(result["budget"], message):
            result["budget"] = "Not mentioned"

        if result["budget"].lower() == "not mentioned":
            found_budget = _extract_budget_from_message(message)
            if found_budget:
                result["budget"] = found_budget

        # Timeline: remove invented values, then add a missed one using rules
        if not _timeline_is_in_message(message):
            result["timeline"] = "Not mentioned"

        if result["timeline"].lower() == "not mentioned":
            found_timeline = _extract_timeline_from_message(message)
            if found_timeline:
                result["timeline"] = found_timeline

        return result

    except Exception as error:
        raise RuntimeError(
            f"Local AI analysis failed: {error}"
        ) from error