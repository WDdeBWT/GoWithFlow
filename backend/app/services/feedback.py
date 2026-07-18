from app.models import Intent


def adjust_intent(intent: Intent, feedback_type: str) -> Intent:
    adjusted = intent.model_copy()

    if feedback_type == "太远了":
        adjusted.time_minutes = max(30, adjusted.time_minutes - 30)
    elif feedback_type == "太热了":
        adjusted.hard_constraints.append("非露天")
        adjusted.soft_preferences.append("凉快")
    elif feedback_type == "太吵了":
        adjusted.soft_preferences.append("安静")
    elif feedback_type == "太网红":
        adjusted.soft_preferences.append("独特")

    return adjusted
