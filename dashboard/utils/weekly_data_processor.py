"""
Weekly data processor for WBS week-based tracking.
Extracts member and team metrics on a weekly basis (Monday-Friday).
"""
from datetime import datetime, date, timedelta
from collections import defaultdict


def get_week_start(dt):
    """Get Monday of the week containing the given date."""
    if isinstance(dt, str):
        dt = datetime.strptime(dt, "%Y-%m-%d").date()
    days_since_monday = dt.weekday()
    return dt - timedelta(days=days_since_monday)


def get_week_label(week_start):
    """Format week as 'Feb 3-7, 2026 (Week 6)'."""
    week_end = week_start + timedelta(days=4)  # Monday to Friday
    week_num = week_start.isocalendar()[1]
    return f"{week_start.strftime('%b %d')}-{week_end.strftime('%d, %Y')} (Week {week_num})"


def get_available_weeks(tasks, weeks_historical=8, weeks_lookahead=4):
    """Get list of available weeks based on task dates."""
    today = date.today()
    current_week = get_week_start(today)
    
    # Historical weeks
    weeks = []
    for i in range(weeks_historical, -1, -1):
        week = current_week - timedelta(weeks=i)
        weeks.append({
            "start": week,
            "label": get_week_label(week),
            "is_current": week == current_week
        })
    
    # Future weeks
    for i in range(1, weeks_lookahead + 1):
        week = current_week + timedelta(weeks=i)
        weeks.append({
            "start": week,
            "label": get_week_label(week),
            "is_current": False
        })
    
    return weeks


def get_weekly_member_data(all_tasks, week_start, config):
    """
    Get member metrics for a specific week.
    
    Returns: {
        "member_id": {
            "name": "Alice Chen",
            "team": "1.6 3DOD",
            "role": "MEM",
            "hours": 17.5,
            "task_count": 12,
            "task_list": ["PCB Design", "Testing", ...],
            "status": "high"  # none/low/ok/high
        }
    }
    """
    week_end = week_start + timedelta(days=4)
    member_data = defaultdict(lambda: {
        "hours": 0,
        "task_count": 0,
        "task_list": [],
        "team": "",
        "role": "MEM",
    })
    
    # Collect tasks that overlap with the week
    for task in all_tasks:
        start_str = task.get("start_date")
        end_str = task.get("end_date")
        
        if not start_str or not end_str:
            continue
        
        try:
            task_start = datetime.strptime(start_str, "%Y-%m-%d").date()
            task_end = datetime.strptime(end_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        
        # Check if task overlaps with the week
        if task_start <= week_end and task_end >= week_start:
            # Distribute hours among resources
            resources = task.get("resources", [])
            if not resources:
                continue
            
            hours_per_resource = task.get("actual_hours", 0) / len(resources)
            
            for resource in resources:
                name = resource if isinstance(resource, str) else str(resource)
                member_data[name]["hours"] += hours_per_resource
                member_data[name]["task_count"] += 1
                member_data[name]["task_list"].append(task["name"])
                
                # Determine role and team
                if not member_data[name]["team"]:
                    member_data[name]["team"] = task.get("group", "Unknown")
                
                if "LEAD" in name.upper():
                    member_data[name]["role"] = "LEAD"
                elif name.startswith("!"):
                    member_data[name]["role"] = "ADMIN"
    
    # Convert to regular dict and add status
    result = {}
    for name, data in member_data.items():
        hours = data["hours"]
        role = data["role"]
        
        # Determine status based on thresholds
        if hours == 0:
            status = "none"
        elif role == "LEAD":
            if hours < config.get("low_hour_lead", 9):
                status = "low"
            elif hours > config.get("high_hour_lead", 20):
                status = "high"
            else:
                status = "ok"
        else:  # Member
            if hours < config.get("low_hour_member", 7):
                status = "low"
            elif hours > config.get("high_hour_member", 15):
                status = "high"
            else:
                status = "ok"
        
        result[name] = {
            "name": name,
            "team": data["team"],
            "role": role,
            "hours": round(hours, 1),
            "task_count": data["task_count"],
            "task_list": data["task_list"],
            "status": status
        }
    
    return result


def get_weekly_team_summary(all_tasks, week_start, config):
    """
    Get team-level summary for a specific week.
    
    Returns: {
        "team_id": {
            "name": "1.6 3DOD",
            "total_hours": 42,
            "member_count": 8,
            "avg_hours_per_member": 5.25,
            "members": [...],
            "status": "low"  # based on avg
        }
    }
    """
    member_data = get_weekly_member_data(all_tasks, week_start, config)
    
    # Group by team
    team_data = defaultdict(lambda: {
        "total_hours": 0,
        "member_count": 0,
        "members": []
    })
    
    for name, member in member_data.items():
        team = member["team"]
        team_data[team]["total_hours"] += member["hours"]
        team_data[team]["member_count"] += 1
        team_data[team]["members"].append(member)
    
    # Convert to regular dict and calculate averages
    result = {}
    for team_name, data in team_data.items():
        avg = data["total_hours"] / max(data["member_count"], 1)
        
        # Determine status based on average hours per member
        if avg < config.get("low_hour_member", 7):
            status = "low"
        else:
            status = "ok"
        
        result[team_name] = {
            "name": team_name,
            "total_hours": round(data["total_hours"], 1),
            "member_count": data["member_count"],
            "avg_hours_per_member": round(avg, 1),
            "members": sorted(data["members"], key=lambda x: -x["hours"]),
            "status": status
        }
    
    return result


def get_upcoming_tasks(all_tasks, weeks_ahead=4):
    """
    Get tasks due in the next N weeks, grouped by week.
    
    Returns: {
        "week_label": [list of tasks],
        ...
    }
    """
    today = date.today()
    current_week = get_week_start(today)
    
    upcoming = defaultdict(list)
    
    for task in all_tasks:
        end_str = task.get("end_date")
        if not end_str or task.get("percent_complete", 0) == 100:
            continue
        
        try:
            task_end = datetime.strptime(end_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        
        # Check if task is due in the next N weeks
        if task_end >= today:
            task_week = get_week_start(task_end)
            weeks_diff = (task_week - current_week).days // 7
            
            if 0 <= weeks_diff < weeks_ahead:
                week_label = get_week_label(task_week)
                upcoming[week_label].append({
                    "name": task["name"],
                    "wbs": task.get("wbs", ""),
                    "group": task.get("group", ""),
                    "end_date": end_str,
                    "days_until_due": (task_end - today).days,
                    "assignees": task.get("resources", []),
                    "progress": task.get("percent_complete", 0)
                })
    
    return dict(upcoming)


def get_member_weekly_history(all_tasks, member_name, weeks=8):
    """
    Get weekly hours breakdown for a specific member.
    
    Returns: [
        {"week": "Feb 3-7", "hours": 12.5, "tasks": 5},
        {"week": "Feb 10-14", "hours": 8.0, "tasks": 3},
        ...
    ]
    """
    today = date.today()
    current_week = get_week_start(today)
    
    history = []
    for i in range(weeks - 1, -1, -1):
        week = current_week - timedelta(weeks=i)
        member_data = get_weekly_member_data(all_tasks, week, {})
        
        if member_name in member_data:
            data = member_data[member_name]
            history.append({
                "week": get_week_label(week).split(" (")[0],  # Just the date range
                "hours": data["hours"],
                "tasks": data["task_count"]
            })
        else:
            history.append({
                "week": get_week_label(week).split(" (")[0],
                "hours": 0,
                "tasks": 0
            })
    
    return history
