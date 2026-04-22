from __future__ import annotations


def score_lead(lead: dict) -> int:
    score = 0

    if lead.get("email"):
        score += 20
    if lead.get("company"):
        score += 10
    if lead.get("source"):
        score += 10

    budget = lead.get("budget") or 0
    if budget >= 5000:
        score += 30
    elif budget >= 1000:
        score += 20
    elif budget > 0:
        score += 10

    urgency = (lead.get("urgency") or "").lower()
    if urgency == "high":
        score += 30
    elif urgency == "medium":
        score += 20
    elif urgency == "low":
        score += 10

    if lead.get("notes"):
        score += 5

    return min(score, 100)
