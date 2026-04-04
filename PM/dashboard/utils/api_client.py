"""
TeamGantt API client wrapper.
Handles authenticated requests to TeamGantt REST API.
Supports live data fetching and writing back to cache.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

BASE_URL = "https://api.teamgantt.com/v1"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


def get_headers():
    # Support all env var names used across scripts
    token = (os.environ.get("TEAMGANTT_TOKEN")
             or os.environ.get("TEAMGANTT_API_TOKEN")
             or os.environ.get("TEAMGANTT_API_KEY", ""))
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_project_id():
    return os.environ.get("PROJECT_ID", "4336931")


def is_api_available():
    """Check if we have a valid API token configured."""
    token = (os.environ.get("TEAMGANTT_TOKEN")
             or os.environ.get("TEAMGANTT_API_TOKEN")
             or os.environ.get("TEAMGANTT_API_KEY", ""))
    return bool(token)


# --- Read endpoints ---

def fetch_project(project_id=None):
    pid = project_id or get_project_id()
    resp = requests.get(f"{BASE_URL}/projects/{pid}", headers=get_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_children_hierarchical(project_id=None):
    """Fetch full hierarchical task tree from TeamGantt API."""
    pid = project_id or get_project_id()
    resp = requests.get(
        f"{BASE_URL}/projects/{pid}/children",
        headers=get_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_children_flat(project_id=None):
    """Fetch flat task list from TeamGantt API."""
    pid = project_id or get_project_id()
    resp = requests.get(
        f"{BASE_URL}/projects/{pid}/children",
        headers=get_headers(),
        params={"is_flat_list": "true"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_task(task_id):
    resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=get_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


# --- Write endpoints ---

def update_estimated_hours(task_id, hours):
    resp = requests.patch(
        f"{BASE_URL}/tasks/{task_id}",
        headers=get_headers(),
        json={"estimated_hours": hours},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def log_time_block(task_id, start_time, end_time):
    resp = requests.post(
        f"{BASE_URL}/times",
        headers=get_headers(),
        json={
            "task_id": task_id,
            "start_time": start_time,
            "end_time": end_time,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


# --- Sync: fetch from API and save to local cache ---

def sync_all(project_id=None):
    """
    Pull latest data from TeamGantt API and save to local data/ directory.
    Returns dict with status of each fetch.
    """
    pid = project_id or get_project_id()
    results = {}

    try:
        data = fetch_children_hierarchical(pid)
        path = os.path.join(DATA_DIR, f"children_hierarchical_{pid}.json")
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        results["hierarchical"] = {"status": "ok", "count": len(data)}
    except Exception as e:
        results["hierarchical"] = {"status": "error", "error": str(e)}

    try:
        data = fetch_children_flat(pid)
        path = os.path.join(DATA_DIR, f"children_flat_{pid}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        results["flat"] = {"status": "ok", "count": len(data)}
    except Exception as e:
        results["flat"] = {"status": "error", "error": str(e)}

    try:
        data = fetch_project(pid)
        path = os.path.join(DATA_DIR, f"project_{pid}.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        results["project"] = {"status": "ok"}
    except Exception as e:
        results["project"] = {"status": "error", "error": str(e)}

    return results
