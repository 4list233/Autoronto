#!/usr/bin/env python3
"""
Delete ONLY time entries that were created by populate_actual_hours.py.
Uses the plan file or execution log to identify script-created entries.
Preserves manually logged hours.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from collections import Counter
from datetime import datetime

# Load env
def load_env():
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()
API_TOKEN = os.getenv('TEAMGANTT_API_KEY', '').strip('"')
PROJECT_ID = os.getenv('TEAMGANTT_PROJECT_ID', '').strip('"')
API_BASE = "https://api.teamgantt.com/v1"
RATE_LIMIT = 0.2

# Default paths (can override with --plan or --log)
PLAN_FILE = Path('/tmp/actual_hours_population_plan.json')
LOG_FILE = Path('/tmp/populate_output.log')

def api_get(path):
    result = subprocess.run([
        'curl', '-s', '--max-time', '30',
        '-H', f'Authorization: Bearer {API_TOKEN}',
        f'{API_BASE}{path}'
    ], capture_output=True, text=True)
    return result.stdout

def api_delete(time_id):
    result = subprocess.run([
        'curl', '-s', '-w', '\n%{http_code}', '-X', 'DELETE',
        '-H', f'Authorization: Bearer {API_TOKEN}',
        f'{API_BASE}/times/{time_id}'
    ], capture_output=True, text=True, timeout=15)
    lines = result.stdout.strip().rsplit('\n', 1)
    return int(lines[1]) if len(lines) > 1 else 0

def user_name_matches(log_name, api_user):
    """Check if log user name matches API user (handles '!Allen Tao - TD' format)."""
    if not api_user:
        return False
    first = api_user.get('first_name', '') or ''
    last = api_user.get('last_name', '') or ''
    api_name = f"{first} {last}".strip()
    api_name_clean = api_name.replace('!', '').strip()
    # "Allen Tao" matches "Allen Tao" or "!Allen Tao - TD"
    return (log_name in api_name or log_name in api_name_clean or
            api_name_clean.endswith(log_name) or
            api_name.replace('!', '').strip().startswith(log_name.split()[0] if log_name else ''))

def task_name_matches(log_task, api_task_name):
    """Log task may be truncated; API has full name."""
    if not log_task or not api_task_name:
        return False
    log_clean = log_task.strip()
    api_clean = (api_task_name or '').strip()
    return (log_clean == api_clean or
            api_clean.startswith(log_clean) or
            log_clean in api_clean)

def compute_hours_from_time(t):
    """Extract hours from a time block (start_time/end_time may be ISO strings or timestamps)."""
    st = t.get('start_time')
    et = t.get('end_time')
    if st is None or et is None:
        return None
    try:
        if isinstance(st, (int, float)) and isinstance(et, (int, float)):
            return round((et - st) / 3600, 1)
        st_str = str(st)
        et_str = str(et)
        start = datetime.fromisoformat(st_str.replace('Z', '+00:00'))
        end = datetime.fromisoformat(et_str.replace('Z', '+00:00'))
        return round((end - start).total_seconds() / 3600, 1)
    except Exception:
        return None

def load_script_entries_from_plan(plan_path):
    """Load (task_id, user_id, date, hours) from plan time_blocks."""
    with open(plan_path) as f:
        data = json.load(f)
    blocks = data.get('time_blocks', [])
    return [(b['task_id'], b['user_id'], b['date'], round(float(b.get('hours', 0)), 1))
            for b in blocks if b.get('user_id') and not str(b.get('task_id', '')).startswith('overhead_')]

def load_script_entries_from_log(log_path):
    """Parse populate_output.log for [N/M] User - Task (Xh)... lines."""
    # Pattern: "  [1/6082] Allen Tao - Preparation (6.3h)..."
    pattern = re.compile(r'\[\d+/\d+\]\s+(.+?)\s+-\s+(.+?)\s+\(([\d.]+)h\)')
    entries = []
    with open(log_path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                user_name = m.group(1).strip()
                task_name = m.group(2).strip()
                if 'Skipping' in task_name:
                    continue
                hours = round(float(m.group(3)), 1)
                entries.append((user_name, task_name, hours))
    return entries

def fetch_all_time_blocks(project_id):
    """Fetch all time blocks for the project. Try project endpoint first, else per-task."""
    url = f'/projects/{project_id}/timeblocks?start_date=2025-07-01&end_date=2026-07-31'
    body = api_get(url)
    time.sleep(RATE_LIMIT)
    try:
        data = json.loads(body)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and 'data' in data:
            return data['data'] if isinstance(data['data'], list) else []
    except Exception:
        pass
    return None

def fetch_timesheets(project_id):
    """Fetch all timesheet entries for project (single API call, project-wide)."""
    data = api_get(f'/projects/{project_id}/children?is_flat_list=true')
    items = json.loads(data)
    tasks = [t for t in items if t.get('type') == 'task']
    task_id_to_name = {t['id']: t['name'] for t in tasks}
    url = f'/timesheets?project_ids[]={project_id}&start_date=2025-07-01&end_date=2026-07-31'
    body = api_get(url)
    time.sleep(RATE_LIMIT)
    rows = json.loads(body) if body else []
    if not isinstance(rows, list):
        return []
    all_entries = []
    seen_ids = set()
    for item in rows:
        task_info = item.get('task', {}) or {}
        tid = item.get('task_id') or task_info.get('id')
        tname = task_info.get('name') or task_id_to_name.get(tid, '')
        for t in item.get('times', []):
            tid_t = t.get('task_id') or tid
            tname_t = t.get('task_name') or tname
            t['_task_id'] = tid_t
            t['_task_name'] = tname_t
            eid = t.get('id')
            if eid and eid not in seen_ids:
                seen_ids.add(eid)
                all_entries.append(t)
    return all_entries

def main():
    import argparse
    p = argparse.ArgumentParser(description='Delete only script-created time entries')
    p.add_argument('--plan', help='Plan JSON with time_blocks (task_id, user_id, date, hours)')
    p.add_argument('--log', help='populate_output.log from execution')
    p.add_argument('-y', '--yes', action='store_true', help='Skip confirmation')
    p.add_argument('--dry-run', action='store_true', help='Only report what would be deleted')
    p.add_argument('--debug', action='store_true', help='Save sample API/log data to /tmp for diagnosis')
    args = p.parse_args()

    plan_path = Path(args.plan) if args.plan else PLAN_FILE
    log_path = Path(args.log) if args.log else LOG_FILE

    # Prefer LOG over plan: the log reflects what was actually executed; the plan may have been overwritten
    script_entries = []
    use_plan_format = False
    source = None

    if log_path.exists():
        try:
            log_entries = load_script_entries_from_log(log_path)
            if log_entries:
                script_entries = log_entries
                use_plan_format = False
                source = f'log ({log_path})'
        except Exception as e:
            print(f"Could not load log: {e}")

    if not script_entries and plan_path.exists():
        try:
            plan_entries = load_script_entries_from_plan(plan_path)
            if plan_entries:
                script_entries = plan_entries
                use_plan_format = True
                source = f'plan ({plan_path})'
        except Exception as e:
            print(f"Could not load plan: {e}")

    if not script_entries:
        print("No script entries found. Need --log or --plan with valid data.")
        print(f"  Log: {log_path} (exists={log_path.exists()})")
        print(f"  Plan: {plan_path} (exists={plan_path.exists()})")
        return 1

    to_delete = Counter(tuple(e) for e in script_entries)

    # Load user name -> user_id from plan (for reliable log-format matching)
    name_to_user_id = {}
    if plan_path.exists() and not use_plan_format:
        try:
            with open(plan_path) as f:
                plan_data = json.load(f)
            for name, info in (plan_data.get('user_summaries') or {}).items():
                uid = info.get('user_id') if isinstance(info, dict) else None
                if uid:
                    name_to_user_id[name] = uid
        except Exception:
            pass
    if name_to_user_id:
        print(f"  Loaded {len(name_to_user_id)} user_ids from plan for matching")

    print()
    print("=" * 60)
    print("Delete script-created hours only (preserve manual entries)")
    print("=" * 60)
    print(f"Source: {source}")
    print(f"Script entries to match: {len(script_entries)}")
    print(f"Date range: 2025-07-01 to 2026-07-31")
    print()

    # Fetch all time blocks
    print("Fetching time blocks from TeamGantt...")
    blocks = fetch_all_time_blocks(PROJECT_ID)
    if blocks is None or len(blocks) == 0:
        print("  Project timeblocks empty or failed, fetching timesheets...")
        data = api_get(f'/projects/{PROJECT_ID}/children?is_flat_list=true')
        items = json.loads(data)
        tasks = [t for t in items if t.get('type') == 'task']
        task_id_to_name = {t['id']: t['name'] for t in tasks}
        time.sleep(RATE_LIMIT)
        entries_flat = fetch_timesheets(PROJECT_ID)
        blocks = entries_flat
        block_format = 'timesheet'
    else:
        block_format = 'timeblock'
        task_id_to_name = {}

    if not blocks:
        print("No time blocks found in project.")
        return 0

    print(f"  Found {len(blocks)} time entries")

    if args.debug:
        debug_dir = Path(__file__).parent / 'debug_output'
        debug_dir.mkdir(exist_ok=True)
        with open(debug_dir / 'debug_raw_blocks.json', 'w') as f:
            json.dump(blocks[:5] if blocks else [], f, indent=2)
        print(f"  [DEBUG] Saved raw blocks to {debug_dir}/")

    # Normalize block structure (timeblocks vs timesheets have different shapes)
    def normalize_block(b):
        if block_format == 'timeblock':
            return {
                'id': b.get('id'),
                'task_id': b.get('task_id'),
                'task_name': b.get('task', {}).get('name') if isinstance(b.get('task'), dict) else (task_id_to_name.get(b.get('task_id'), '')),
                'user': b.get('user', {}),
                'user_id': (b.get('user') or {}).get('id') if isinstance(b.get('user'), dict) else b.get('user_id'),
                'start_time': b.get('start_time'),
                'end_time': b.get('end_time'),
            }
        else:
            user = b.get('user')
            uid = b.get('user_id')
            if uid is None and isinstance(user, dict):
                uid = user.get('id')
            if uid is None and isinstance(user, (int, float)):
                uid = int(user)
            return {
                'id': b.get('id'),
                'task_id': b.get('_task_id', b.get('task_id')),
                'task_name': b.get('_task_name', (b.get('task') or {}).get('name') if isinstance(b.get('task'), dict) else ''),
                'user': user if isinstance(user, dict) else {},
                'user_id': uid,
                'start_time': b.get('start_time'),
                'end_time': b.get('end_time'),
            }

    to_delete_ids = []
    normalized_samples = []  # for debug
    for b in blocks:
        nb = normalize_block(b)
        if args.debug and len(normalized_samples) < 5:
            normalized_samples.append({**nb, 'hours': compute_hours_from_time(nb)})
        entry_id = nb['id']
        if not entry_id:
            continue
        entry_task_id = nb['task_id']
        entry_task_name = nb['task_name'] or task_id_to_name.get(entry_task_id, '')
        entry_user = nb['user'] if isinstance(nb.get('user'), dict) else {}
        entry_user_id = nb['user_id'] or (entry_user.get('id') if entry_user else None)
        entry_hours = compute_hours_from_time(nb)
        entry_date = (str(nb.get('start_time') or ''))[:10]

        if use_plan_format:
            key = (entry_task_id, entry_user_id, entry_date, entry_hours)
            if key in to_delete and to_delete[key] > 0:
                to_delete[key] -= 1
                if to_delete[key] == 0:
                    del to_delete[key]
                to_delete_ids.append(entry_id)
        else:
            # Log format: match by (user_name, task_name, hours)
            best_key = None
            for key in list(to_delete.keys()):
                if to_delete[key] <= 0:
                    continue
                un, tn, hr = key
                if entry_hours is None or abs(entry_hours - hr) >= 0.35:
                    continue
                if not task_name_matches(tn, entry_task_name):
                    continue
                # Match user: prefer user_id from plan, else name match
                user_match = False
                if name_to_user_id and entry_user_id is not None:
                    target_uid = name_to_user_id.get(un)
                    user_match = target_uid == entry_user_id
                if not user_match:
                    user_match = user_name_matches(un, entry_user)
                if user_match:
                    best_key = key
                    break
            if best_key:
                to_delete[best_key] -= 1
                if to_delete[best_key] == 0:
                    del to_delete[best_key]
                to_delete_ids.append(entry_id)

    if args.debug:
        debug_dir = Path(__file__).parent / 'debug_output'
        debug_dir.mkdir(exist_ok=True)
        with open(debug_dir / 'debug_normalized_blocks.json', 'w') as f:
            json.dump(normalized_samples, f, indent=2)
        with open(debug_dir / 'debug_log_samples.json', 'w') as f:
            json.dump(dict(list(to_delete.most_common(30))), f, indent=2)
        print(f"  [DEBUG] Saved to {debug_dir}/")

    print(f"\nEntries to delete (script-created): {len(to_delete_ids)}")
    remaining = sum(to_delete.values())
    if remaining > 0:
        print(f"  (Note: {remaining} log entries had no matching API record)")

    if not to_delete_ids:
        print("No matching entries found. Nothing to delete.")
        return 0

    if args.dry_run:
        print("\n[DRY RUN] Would delete the above entries. Run without --dry-run to execute.")
        return 0

    if not args.yes:
        confirm = input("Proceed? [y/N]: ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return 0

    deleted = failed = 0
    for j, tid in enumerate(to_delete_ids):
        status = api_delete(tid)
        if status in (200, 204):
            deleted += 1
        else:
            failed += 1
        time.sleep(RATE_LIMIT)
        if (j + 1) % 100 == 0:
            print(f"  Deleted {j+1}/{len(to_delete_ids)} ({deleted} ok, {failed} fail)")

    print()
    print(f"Done: {deleted} deleted, {failed} failed")

if __name__ == '__main__':
    sys.exit(main() or 0)
