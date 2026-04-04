#!/usr/bin/env python3
"""Quick script to fetch sample API responses for debugging delete logic."""
import json
import os
import subprocess
from pathlib import Path

# Load env
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"')

API_TOKEN = os.environ.get('TEAMGANTT_API_KEY', '')
PROJECT_ID = os.environ.get('TEAMGANTT_PROJECT_ID', '')
API_BASE = "https://api.teamgantt.com/v1"

def get(path):
    r = subprocess.run(['curl', '-s', '-H', f'Authorization: Bearer {API_TOKEN}', f'{API_BASE}{path}'],
                      capture_output=True, text=True, timeout=30)
    return r.stdout

# 1. Get one task
data = json.loads(get(f'/projects/{PROJECT_ID}/children?is_flat_list=true'))
tasks = [t for t in data if t.get('type') == 'task']
task = tasks[0] if tasks else {}
tid = task.get('id')
tname = task.get('name', '')
print(f"Task: {tid} - {tname}")

# 2. Timesheets for that task
ts = get(f'/timesheets?task_ids[]={tid}&start_date=2025-07-01&end_date=2026-07-31')
ts_data = json.loads(ts)
print(f"\nTimesheets response type: {type(ts_data)}")
print(f"Timesheets length: {len(ts_data) if isinstance(ts_data, list) else 'N/A'}")
out_dir = Path(__file__).parent / 'debug_output'
out_dir.mkdir(exist_ok=True)
with open(out_dir / 'timesheets_sample.json', 'w') as f:
    json.dump(ts_data[:3] if isinstance(ts_data, list) and len(ts_data) > 3 else ts_data, f, indent=2)
print(f"Saved to {out_dir}/timesheets_sample.json")

# 3. Time blocks for that task (GET /tasks/{id}/times)
tb = get(f'/tasks/{tid}/times')
try:
    tb_data = json.loads(tb)
    with open(out_dir / 'task_times_sample.json', 'w') as f:
        json.dump(tb_data if isinstance(tb_data, list) else [tb_data], f, indent=2)
    print(f"Task times type: {type(tb_data)}, len: {len(tb_data) if isinstance(tb_data, list) else 'N/A'}")
    print(f"Saved to {out_dir}/task_times_sample.json")
except Exception as e:
    print(f"Task times error: {e}")
