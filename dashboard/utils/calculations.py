"""
Rollup calculations, variance analysis, and progress computations.
"""
from datetime import datetime, date, timedelta


def calculate_variance(estimated, actual):
    """Calculate variance percentage: (Actual - Estimated) / Estimated."""
    if estimated == 0:
        return 0
    return round(((actual - estimated) / estimated) * 100, 1)


def calculate_weighted_progress(tasks):
    """Calculate average progress across tasks."""
    if tasks:
        return sum(t.get("percent_complete", 0) for t in tasks) / len(tasks)
    return 0


def get_status_emoji(progress, on_track=75, at_risk=50):
    """Return status emoji based on progress thresholds."""
    if progress >= on_track:
        return "🟢"
    elif progress >= at_risk:
        return "🟡"
    return "🔴"


def get_status_label(progress, on_track=75, at_risk=50):
    if progress >= on_track:
        return "On Track"
    elif progress >= at_risk:
        return "At Risk"
    return "Behind"


def days_overdue(end_date_str):
    """Return number of days a task is overdue (negative = not yet due)."""
    if not end_date_str:
        return 0
    try:
        end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return (date.today() - end).days
    except (ValueError, TypeError):
        return 0


def is_overdue(end_date_str):
    return days_overdue(end_date_str) > 0


def detect_task_issues(task, config):
    """Detect issues with a task. Returns list of issue strings."""
    issues = []

    # Milestones are checkpoints, not work items — skip issue detection
    if task.get("type") == "milestone":
        return issues

    overdue = days_overdue(task.get("end_date"))
    if overdue > config.get("overdue_critical_days", 7):
        issues.append(f"Overdue by {overdue} days (CRITICAL)")
    elif overdue > 0:
        issues.append(f"Overdue by {overdue} days")

    if task.get("actual_hours", 0) > 0 and task.get("percent_complete", 0) == 0:
        issues.append("Hours logged but 0% progress")

    if not task.get("resources") or len(task.get("resources", [])) == 0:
        issues.append("Unassigned")

    return issues


def categorize_alert(issues):
    """Categorize alert as critical or warning."""
    critical_keywords = ["CRITICAL", "0% progress"]
    for issue in issues:
        for kw in critical_keywords:
            if kw in issue:
                return "critical"
    if issues:
        return "warning"
    return "none"
