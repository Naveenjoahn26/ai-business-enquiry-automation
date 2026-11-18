def generate_response(customer_name, analysis):

    category = analysis["category"]
    requirement = analysis["requirement"]
    budget = analysis["budget"]
    timeline = analysis["timeline"]
    urgency = analysis["urgency"]

    response = f"""[DRAFT - Pending human approval. Do not send automatically.]

Dear {customer_name},

Thank you for contacting Curd Rice Business Studio.

We have received your enquiry regarding {category}.

Your requirement:
{requirement}
"""

    if budget != "Not mentioned":
        response += f"\nBudget mentioned by you: {budget}\n"

    if timeline != "Not mentioned":
        response += f"Timeline mentioned by you: {timeline}\n"

    if urgency == "Urgent":
        response += "\nWe have noted that this enquiry is urgent.\n"

    response += """
A member of our team will review your enquiry and respond to you.

Regards,
Curd Rice Business Studio
"""

    return response