
def generate_response(customer_name, analysis):

    category = analysis["category"]
    requirement = analysis["requirement"]
    budget = analysis["budget"]
    timeline = analysis["timeline"]
    urgency = analysis["urgency"]

    response = f"""
Dear {customer_name},

Thank you for contacting us!

We have received your enquiry regarding {category}.

Your requirement:
{requirement}
"""

    if budget != "Not mentioned":
        response += f"\nYour mentioned budget: {budget}\n"

    if timeline != "Not mentioned":
        response += f"Your expected timeline: {timeline}\n"

    if urgency == "Urgent":
        response += "\nWe understand that this is an urgent requirement.\n"

    response += """
Our team will review your requirements and get back to you shortly.

Regards,
Business Team
"""

    return response
