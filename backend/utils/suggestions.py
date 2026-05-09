def generate_suggestions(input_data, risk_level):
    """
    Generate retention suggestions based on customer input data and risk level.
    """
    suggestions = []

    # If the risk level is low, return a positive message
    if risk_level == "Low":
        suggestions.append("Customer is currently happy. Maintain regular positive engagement.")
        return suggestions

    # Generate suggestions for High or Medium risk
    if int(input_data.get("support_calls", 0)) >= 3:
        suggestions.append("Improve customer support experience - follow up on recent support tickets.")

    if int(input_data.get("payment_delay", 0)) >= 10:
        suggestions.append("Offer flexible payment options or a one-time late fee waiver.")

    if input_data.get("contract_length", "Monthly") == "Monthly":
        suggestions.append("Promote yearly subscription discounts to increase commitment.")

    if int(input_data.get("tenure", 0)) <= 6:
        suggestions.append("Provide onboarding benefits or personalized tutorials.")

    if input_data.get("subscription_type", "Basic") == "Basic":
        suggestions.append("Recommend premium features with a free 1-month trial.")
        
    if int(input_data.get("usage_frequency", 0)) <= 5:
        suggestions.append("Send a re-engagement email highlighting new features or popular content.")

    # Fallback if no specific condition is met
    if not suggestions:
        suggestions.append("Schedule a check-in call to understand their needs better.")

    return suggestions
