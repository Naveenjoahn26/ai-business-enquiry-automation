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
    """Backup rules used when the AI gives a category that is not in our list."""
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


def _final_category(ai_category, message):
    # Clear job / internship messages are decided by Python rules
    if _is_job_or_internship(message):
        return "Job / Internship"

    # Accept the AI category only if it is exactly one from our list
    for category in CATEGORIES:
        if ai_category.strip().lower() == category.lower():
            return category

    # Otherwise use backup keyword rules
    return _category_from_keywords(message)


def classify_enquiry(message):

    categories_text = "\n".join(f"- {c}" for c in CATEGORIES)

    prompt = f"""
You are an expert business enquiry analyst.

Read the customer's message carefully:
{message}

Extract information ONLY from the customer's message.

Rules:
1. "category" MUST be exactly one item from this list:
{categories_text}
2. Describe the customer's actual requirement in one sentence.
3. Extract the exact budget ONLY if the customer wrote it. Otherwise write "Not mentioned".
4. Extract the timeline ONLY if the customer wrote it. Otherwise write "Not mentioned".
5. Set urgency to "Urgent" only if the customer indicates urgency.
6. Never invent a budget or timeline. Never copy values from the example.

Example:
Input: We want a new website for our school.

Expected JSON:
{{
  "category": "Website & App Development",
  "requirement": "Build a new website for a school",
  "budget": "Not mentioned",
  "timeline": "Not mentioned",
  "urgency": "Normal"
}}

Now analyse the customer's message and return only JSON with these five fields:
category, requirement, budget, timeline, urgency.
"""

    payload = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": "Extract business enquiry details accurately. Choose the category only from the given list. Never invent budget or timeline."
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

        # Category must be from our fixed list
        result["category"] = _final_category(result["category"], message)

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

        if result["requirement"].lower() == "customer requirement":
            raise ValueError("AI returned placeholder requirement")

        return result

    except Exception as error:
        raise RuntimeError(
            f"Local AI analysis failed: {error}"
        ) from error