"""
Outlier detection for over/under-contributing members.
"""


def detect_outliers(resources, config):
    """
    Detect members who are over or under-contributing based on config thresholds.
    Returns dict with 'under' and 'over' lists.
    """
    under = []
    over = []

    for res in resources:
        role = res.get("role", "MEM")
        avg_hours = res.get("total_hours", 0)

        if role == "LEAD":
            low_threshold = config.get("low_hour_lead", 9)
            high_threshold = config.get("high_hour_lead", 20)
        else:
            low_threshold = config.get("low_hour_member", 7)
            high_threshold = config.get("high_hour_member", 15)

        if avg_hours < low_threshold and role != "ADMIN":
            under.append({
                **res,
                "threshold": low_threshold,
                "deficit": round(low_threshold - avg_hours, 1),
            })
        elif avg_hours > high_threshold:
            over.append({
                **res,
                "threshold": high_threshold,
                "surplus": round(avg_hours - high_threshold, 1),
            })

    return {"under": under, "over": over}
