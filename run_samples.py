import json
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/analyse"

SAMPLES = {
    "001": "We are a jewellery business looking for an AI-powered WhatsApp customer support system.",
    "002": "Need a website for our manufacturing company. Budget is ₹2 lakh. Can we discuss this week?",
    "003": "What services do you offer?",
    "004": "We want to automate our inventory and dispatch operations.",
    "005": "Looking for a digital marketing internship.",
    "006": "We are interested in developing an ERP system for our silver jewellery business.",
    "007": "Your services look interesting. Please send your pricing details.",
    "008": "Need AI automation for handling 500 customer enquiries per day. We want to start immediately.",
    "009": "I am a student looking for a college project opportunity.",
    "010": "We need an AI assistant that can read documents and answer questions from our internal company data.",
    "011": "I want to partner with your company for a business opportunity.",
    "012": "I am unhappy with the service received and need someone to call me urgently.",
}

for enquiry_id, message in SAMPLES.items():
    payload = {
        "customer_name": f"Test Customer {enquiry_id}",
        "email": f"test{enquiry_id}@example.com",
        "message": message,
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print("=" * 70)
    print(f"[{enquiry_id}] {message}")

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))

        analysis = data["analysis"]
        score = data["lead_score"]
        review = data["human_review"]

        print(f"  Category : {analysis['category']}")
        print(f"  Budget   : {analysis['budget']}")
        print(f"  Timeline : {analysis['timeline']}")
        print(f"  Urgency  : {analysis['urgency']}")
        print(f"  Score    : {score['score']} ({score['priority']})")
        print(f"  Human review: {review['needs_human_review']}")
        for reason in review["reasons"]:
            print(f"     - {reason}")

    except urllib.error.HTTPError as error:
        print(f"  FAILED: HTTP {error.code}")
    except Exception as error:
        print(f"  FAILED: {error}")

print("=" * 70)
print("Done")