"""
Data loader for TeamGantt data.
Supports two modes:
  - "live": Fetches directly from TeamGantt API on every load
  - "cached" (default): Reads from local JSON files in data/
Toggle via config.json "data_source" key or the Settings page.
"""
import json
import os
import pandas as pd
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)


def _use_live():
    """Check if config says to use live API."""
    config = load_config()
    return config.get("data_source", "cached") == "live"


def load_hierarchical_data():
    config = load_config()
    pid = config.get("project_id", "4336931")

    if _use_live():
        from .api_client import fetch_children_hierarchical
        return fetch_children_hierarchical(pid)

    path = os.path.join(DATA_DIR, f"children_hierarchical_{pid}.json")
    with open(path, "r") as f:
        return json.load(f)


def load_flat_data():
    config = load_config()
    pid = config.get("project_id", "4336931")

    if _use_live():
        from .api_client import fetch_children_flat
        return fetch_children_flat(pid)

    path = os.path.join(DATA_DIR, f"children_flat_{pid}.json")
    with open(path, "r") as f:
        return json.load(f)


def load_project_data():
    config = load_config()
    pid = config.get("project_id", "4336931")

    if _use_live():
        from .api_client import fetch_project
        return fetch_project(pid)

    path = os.path.join(DATA_DIR, f"project_{pid}.json")
    with open(path, "r") as f:
        return json.load(f)


def get_all_tasks(data=None):
    """Extract all tasks from hierarchical data into a flat list with group info."""
    if data is None:
        data = load_hierarchical_data()

    all_tasks = []

    def collect(items, parent_group="", parent_group_id=None, depth=0):
        for item in items:
            if item.get("type") in ("task", "milestone"):
                resources = item.get("resources", [])
                resource_names = [r.get("name", "") for r in resources]
                leads = [n for n in resource_names if "LEAD" in n.upper() or n.startswith("!")]
                members = [n for n in resource_names if n not in leads]

                all_tasks.append({
                    "id": item.get("id"),
                    "name": item.get("name", ""),
                    "type": item.get("type", "task"),
                    "wbs": item.get("wbs", ""),
                    "group": parent_group,
                    "group_id": parent_group_id,
                    "estimated_hours": item.get("estimated_hours") or 0,
                    "actual_hours": item.get("actual_hours") or 0,
                    "percent_complete": item.get("percent_complete") or 0,
                    "start_date": item.get("start_date"),
                    "end_date": item.get("end_date"),
                    "resources": resource_names,
                    "leads": leads,
                    "members": members,
                    "dependencies": item.get("dependencies", []),
                    "is_critical": item.get("is_critical", False),
                    "has_tracked_time": item.get("has_tracked_time", False),
                    "depth": depth,
                })
            if "children" in item:
                gname = item.get("name", parent_group) if item.get("type") == "group" else parent_group
                gid = item.get("id", parent_group_id) if item.get("type") == "group" else parent_group_id
                collect(item["children"], gname, gid, depth + (1 if item.get("type") == "group" else 0))

    collect(data)
    return all_tasks


def get_teams(data=None):
    """Get top-level team groups with aggregated metrics."""
    if data is None:
        data = load_hierarchical_data()

    all_tasks = get_all_tasks(data)
    teams = []

    for group in data:
        if group.get("type") != "group":
            continue

        team_name = group.get("name", "Unknown")
        team_id = group.get("id")
        team_tasks = [t for t in all_tasks if t["group"] == team_name]

        total_tasks = len(team_tasks)
        completed = len([t for t in team_tasks if t["percent_complete"] == 100])
        in_progress = len([t for t in team_tasks if 0 < t["percent_complete"] < 100])
        not_started = len([t for t in team_tasks if t["percent_complete"] == 0])

        total_est = sum(t["estimated_hours"] for t in team_tasks)
        total_act = sum(t["actual_hours"] for t in team_tasks)

        # Weighted progress
        if total_est > 0:
            progress = sum(t["percent_complete"] * t["estimated_hours"] for t in team_tasks) / total_est
        elif total_tasks > 0:
            progress = sum(t["percent_complete"] for t in team_tasks) / total_tasks
        else:
            progress = 0

        # Collect unique resources
        all_resources = set()
        all_leads = set()
        for t in team_tasks:
            all_resources.update(t["resources"])
            all_leads.update(t["leads"])

        # Status
        config = load_config()
        if progress >= config["on_track_progress"]:
            status = "On Track"
            status_color = "green"
        elif progress >= config["at_risk_progress"]:
            status = "At Risk"
            status_color = "orange"
        else:
            status = "Behind"
            status_color = "red"

        teams.append({
            "id": team_id,
            "name": team_name,
            "start_date": group.get("start_date"),
            "end_date": group.get("end_date"),
            "total_tasks": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "estimated_hours": total_est,
            "actual_hours": total_act,
            "progress": round(progress, 1),
            "resources": list(all_resources),
            "leads": list(all_leads),
            "member_count": len(all_resources),
            "status": status,
            "status_color": status_color,
        })

    return teams


def get_all_resources(data=None):
    """Get all unique resources with their roles and team assignments."""
    if data is None:
        data = load_hierarchical_data()

    all_tasks = get_all_tasks(data)
    resource_map = {}

    for task in all_tasks:
        for res in task.get("resources", []):
            name = res if isinstance(res, str) else res
            if name not in resource_map:
                is_lead = "LEAD" in name.upper()
                is_admin = name.startswith("!")
                role = "ADMIN" if is_admin else ("LEAD" if is_lead else "MEM")
                # Extract team prefix
                team = name.split(" - ")[0] if " - " in name else task["group"]
                resource_map[name] = {
                    "name": name,
                    "role": role,
                    "team": team,
                    "tasks": [],
                    "total_hours": 0,
                }
            resource_map[name]["tasks"].append(task["name"])
            resource_map[name]["total_hours"] += task.get("actual_hours", 0) / max(len(task["resources"]), 1)

    return list(resource_map.values())


def get_all_members_with_metrics(data=None):
    """
    Get all members with their task and hour metrics across all time.
    Returns a list suitable for All Members Overview page.
    """
    if data is None:
        data = load_hierarchical_data()
    
    all_tasks = get_all_tasks(data)
    resources = get_all_resources(data)
    
    members = []
    for resource in resources:
        members.append({
            "name": resource["name"],
            "team": resource["team"],
            "role": resource["role"],
            "total_hours": round(resource["total_hours"], 1),
            "task_count": len(resource["tasks"]),
            "task_list": resource["tasks"]
        })
    
    return members


def get_member_weekly_breakdown(member_name, data=None, weeks=8):
    """Get weekly hours breakdown for a specific member."""
    if data is None:
        data = load_hierarchical_data()
    
    all_tasks = get_all_tasks(data)
    from .weekly_data_processor import get_member_weekly_history
    return get_member_weekly_history(all_tasks, member_name, weeks)


def get_project_summary(data=None):
    """Get high-level project summary metrics."""
    if data is None:
        data = load_hierarchical_data()

    config = load_config()
    all_tasks = get_all_tasks(data)
    teams = get_teams(data)

    total_tasks = len(all_tasks)
    completed = len([t for t in all_tasks if t["percent_complete"] == 100])
    in_progress = len([t for t in all_tasks if 0 < t["percent_complete"] < 100])
    not_started = len([t for t in all_tasks if t["percent_complete"] == 0])

    total_est = sum(t["estimated_hours"] for t in all_tasks)
    total_act = sum(t["actual_hours"] for t in all_tasks)

    if total_tasks > 0:
        avg_progress = sum(t["percent_complete"] for t in all_tasks) / total_tasks
    else:
        avg_progress = 0

    today = date.today()
    comp_date = datetime.strptime(config["competition_date"], "%Y-%m-%d").date()
    workshop_date = datetime.strptime(config["winter_workshop_date"], "%Y-%m-%d").date()
    days_to_competition = (comp_date - today).days
    days_to_workshop = (workshop_date - today).days

    teams_behind = len([t for t in teams if t["status"] == "Behind"])
    teams_at_risk = len([t for t in teams if t["status"] == "At Risk"])

    overdue_tasks = []
    for t in all_tasks:
        if t["end_date"] and t["percent_complete"] < 100:
            try:
                end = datetime.strptime(t["end_date"], "%Y-%m-%d").date()
                if end < today:
                    overdue_tasks.append(t)
            except (ValueError, TypeError):
                pass

    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "not_started": not_started,
        "total_estimated_hours": total_est,
        "total_actual_hours": total_act,
        "avg_progress": round(avg_progress, 1),
        "days_to_competition": days_to_competition,
        "days_to_workshop": days_to_workshop,
        "teams_behind": teams_behind,
        "teams_at_risk": teams_at_risk,
        "overdue_tasks": len(overdue_tasks),
        "total_resources": len(get_all_resources(data)),
        "total_teams": len(teams),
    }
