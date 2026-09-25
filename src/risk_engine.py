

from datetime import date
from typing import Any


SEVERITY_POINTS = {
    "Low": 5,
    "Medium": 15,
    "High": 30,
}


def _days_late(planned_completion: str, forecast_completion: str) -> int:
    """Return the number of forecast delay days, or zero when not delayed."""
    planned = date.fromisoformat(planned_completion)
    forecast = date.fromisoformat(forecast_completion)
    return max((forecast - planned).days, 0)


def calculate_risk_score(project: dict[str, Any]) -> dict[str, Any]:
    """Calculate a transparent risk score for one project."""
    score = 0
    evidence: list[str] = []
    open_risks = [
        risk for risk in project.get("risks", [])
        if risk.get("status") == "Open"
    ]
    open_issues = [
        issue for issue in project.get("issues", [])
        if issue.get("status") == "Open"
    ]

    for item in [*open_risks, *open_issues]:
        severity = item.get("severity", "Low")
        points = SEVERITY_POINTS.get(severity, 0)
        score += points
        evidence.append(f"{severity} open item: {item.get('description', 'Unspecified')}")

    delay_days = _days_late(
        project["schedule"]["planned_completion"],
        project["schedule"]["forecast_completion"],
    )

    if delay_days > 0:
        score += min(delay_days, 30)
        evidence.append(f"Forecast completion is {delay_days} days late")

    planned_budget = project["budget"]["planned"]
    spent_budget = project["budget"]["spent"]
    budget_usage = spent_budget / planned_budget if planned_budget else 0

    if budget_usage >= 0.90:
        score += 25
        evidence.append(f"Budget usage is {budget_usage:.0%}")
    elif budget_usage >= 0.75:
        score += 10
        evidence.append(f"Budget usage is {budget_usage:.0%}")

    if score >= 70:
        rating = "Red"
        recommended_action = "Escalate immediately and establish a corrective action plan."
    elif score >= 35:
        rating = "Amber"
        recommended_action = "Review risks with the project leadership team this week."
    else:
        rating = "Green"
        recommended_action = "Continue monitoring through normal governance."

    return {
        "project_id": project["project_id"],
        "project_name": project["project_name"],
        "rating": rating,
        "score": score,
        "evidence": evidence,
        "open_risk_count": len(open_risks),
        "open_issue_count": len(open_issues),
        "budget_usage": round(budget_usage, 3),
        "schedule_delay_days": delay_days,
        "recommended_action": recommended_action,
    }
