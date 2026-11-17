
import json
import urllib.request


def classify_enquiry(message):

    prompt = f"""
You are an expert business enquiry analyst.

Read the customer's message carefully:
{message}

Extract information ONLY from the customer's message.

Rules:
1. Identify the actual service or product requested.
2. Write a meaningful category, for example "AI Chatbot", "Website Development", or "ERP Software".
3. Describe the customer's actual requirement in one sentence.
4. Extract the exact budget if mentioned. Otherwise write "Not mentioned".
5. Extract the timeline if mentioned. Otherwise write "Not mentioned".
6. Set urgency to "Urgent" only if the customer indicates urgency.
7. Never return placeholder text like "enquiry category" or "customer requirement".

Example:
Input: We need an AI chatbot urgently. Budget is 50000 and delivery within 15 days.

Expected JSON:
{{
  "category": "AI Chatbot",
  "requirement": "Develop an AI chatbot",
  "budget": "50000",
  "timeline": "15 days",
  "urgency": "Urgent"
}}

Now analyse the customer's message and return only JSON with these five fields:
category, requirement, budget, timeline, urgency.
"""

    payload = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": "Extract business enquiry details accurately. Never copy placeholders."
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

        required_fields = [
            "category", "requirement", "budget",
            "timeline", "urgency"
        ]

        if not all(field in result for field in required_fields):
            raise ValueError("AI response is missing required fields")

        if result["urgency"] not in ["Urgent", "Normal"]:
            raise ValueError("Invalid urgency value")

        if result["category"].lower() == "enquiry category":
            raise ValueError("AI returned placeholder category")

        if result["requirement"].lower() == "customer requirement":
            raise ValueError("AI returned placeholder requirement")

        return result

    except Exception as error:
        raise RuntimeError(
            f"Local AI analysis failed: {error}"
        ) from error
