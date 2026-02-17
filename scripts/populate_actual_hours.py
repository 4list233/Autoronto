#!/usr/bin/env python3
"""
Populate actual hours for TeamGantt project based on role-based distributions
and UofT academic calendar.

Features:
- Role-based hour sampling (Chad/TD/Lead/Member/Inactive)
- UofT academic calendar awareness (reading weeks, study weeks, exams)
- Week-by-week hour allocation
- TD overhead task handling
- Realistic time block distribution
"""

import json
import os
import sys
import time
import subprocess
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables
def load_env():
    """Load .env file from project root."""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# API Configuration
API_TOKEN = os.getenv('TEAMGANTT_API_KEY', '').strip('"')
PROJECT_ID = int(os.getenv('TEAMGANTT_PROJECT_ID', '0').strip('"'))
API_BASE = "https://api.teamgantt.com/v1"
DRY_RUN = True  # Set to False to actually execute
RATE_LIMIT_DELAY = 0.25  # seconds between API calls

# Validate configuration
if not API_TOKEN:
    print("❌ ERROR: TEAMGANTT_API_KEY not found")
    print("Please create a .env file with: TEAMGANTT_API_KEY=your_token_here")
    sys.exit(1)

if not PROJECT_ID:
    print("❌ ERROR: TEAMGANTT_PROJECT_ID not found")
    sys.exit(1)

# Role-based distributions (hours per week)
# max_hours = hard cap per week for this role
ROLE_DISTRIBUTIONS = {
    'chad_phd': {
        'mean': 12.0,
        'std_dev': 1.5,
        'max_hours': 15.0,
        'calendar_type': 'phd',
        'description': 'PhD student - 9-15h/week year-round'
    },
    'td': {
        'mean': 12.0,
        'std_dev': 1.5,
        'max_hours': 15.0,
        'calendar_type': 'undergrad',
        'overhead_percentage': 0.375,
        'description': 'Technical Director - 9-15h/week + overhead'
    },
    'lead': {
        'mean': 10.5,
        'std_dev': 1.25,
        'max_hours': 13.0,
        'calendar_type': 'undergrad',
        'description': 'Team lead - 8-13h/week'
    },
    'member': {
        'mean': 8.5,
        'std_dev': 0.75,
        'max_hours': 10.0,
        'calendar_type': 'undergrad',
        'description': 'Regular member - 7-10h/week'
    },
    'inactive': {
        'mean': 3.0,
        'std_dev': 1.5,
        'max_hours': 6.0,
        'calendar_type': 'undergrad',
        'description': 'Inactive/struggling - 0-6h/week'
    },
    'quit': {
        'mean': 0,
        'std_dev': 0,
        'max_hours': 0,
        'calendar_type': 'none',
        'description': 'Has quit - no contribution'
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_json_config(filename):
    """Load JSON configuration file."""
    path = Path(__file__).parent / filename
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: {filename} not found")
        print(f"Expected at: {path}")
        sys.exit(1)

def extract_person_name(tg_display_name):
    """
    Extract clean person name from TeamGantt display name.
    Handles all formatting variations:
      - "TEAM - Name - ROLE"       (standard)
      - "!Name - TD"               (! prefix)
      - "!Name"                    (no role suffix)
      - "GUI – Name – MEM"        (em-dash)
      - "DRIVERS Name - MEM"      (missing first separator)
      - "DRIVERS - Name -MEM"     (missing space before role)
      - "SIM  - Name - MEM"       (double space)
      - "Name"                    (plain name)
    """
    # Normalize: replace em-dashes with regular dashes, strip !
    clean = tg_display_name.replace('\u2013', '-').replace('\u2014', '-').replace('!', '').strip()
    
    # Normalize multiple spaces
    while '  ' in clean:
        clean = clean.replace('  ', ' ')
    
    # Known teams and roles
    teams = {'SIM', 'VIE', 'MI', 'DLA', 'DRIVERS', 'LOC', 'MAP', 'MARKETING',
             'PLAN', 'PLANNING', 'RESEARCH', 'SS', 'TRACKING', '2DOD', '3DOD',
             'GUI', 'MECH', 'aUToronto PM', 'aUToronto'}
    roles = {'TD', 'LEAD', 'MEM', 'Member', 'LEAAD', 'PM'}
    
    # Split by ' - ' (standard separator)
    parts = [p.strip() for p in clean.split(' - ')]
    
    # Filter out known team/role tokens
    person_parts = []
    for part in parts:
        if part in teams or part in roles:
            continue
        # Strip role suffixes stuck to name (e.g. "Mahmoud Anklis -MEM" -> after split gives "Mahmoud Anklis -MEM")
        for role in roles:
            if part.endswith(f'-{role}') or part.endswith(f' {role}'):
                part = part[:-(len(role))].rstrip(' -')
            if part.endswith(f'- {role}'):
                part = part[:-(len(role) + 2)].strip()
        # Strip team prefixes stuck to name (e.g. "DRIVERS Jonathan Zhu")
        for team in sorted(teams, key=len, reverse=True):
            if part.upper().startswith(team.upper() + ' '):
                part = part[len(team):].strip()
        if part and part not in teams and part not in roles:
            person_parts.append(part)
    
    return ' '.join(person_parts).strip() if person_parts else clean

def fetch_project_data():
    """
    Fetch fresh task data and user mapping directly from TeamGantt API.
    Returns:
        (tasks_list, user_id_map, tg_display_names)
        - tasks_list: list of task dicts with resources
        - user_id_map: {person_name: user_id}
        - tg_display_names: {user_id: tg_display_name}
    """
    print("  Fetching project data from TeamGantt API...")
    cmd = [
        'curl', '-s',
        '-H', f'Authorization: Bearer {API_TOKEN}',
        f'{API_BASE}/projects/{PROJECT_ID}/children?is_flat_list=true'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    all_items = json.loads(result.stdout)
    
    # Separate tasks from groups
    tasks = [t for t in all_items if t.get('type') == 'task']
    
    # Build user_id mappings from resources
    tg_display_names = {}  # user_id -> display_name
    user_id_map = {}       # person_name -> user_id
    
    for item in all_items:
        for r in item.get('resources', []):
            if r.get('type') == 'user':
                uid = r['type_id']
                display_name = r['name']
                tg_display_names[uid] = display_name
                person_name = extract_person_name(display_name)
                user_id_map[person_name] = uid
    
    print(f"  ✓ Fetched {len(tasks)} tasks, {len(user_id_map)} users from API")
    return tasks, user_id_map, tg_display_names

def get_week_start(date):
    """Get Monday of the week for a given date."""
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
    elif isinstance(date, datetime):
        date = date.date()
    
    # Get Monday (weekday 0)
    days_since_monday = date.weekday()
    monday = date - timedelta(days=days_since_monday)
    return monday

def get_week_label(week_start):
    """Format week label for display."""
    return week_start.strftime('%Y-%m-%d')

def get_week_modifier(week_start, calendar_type, academic_calendar):
    """
    Get calendar modifier for given week based on user's calendar type.
    
    Args:
        week_start: Monday of the week (datetime.date)
        calendar_type: 'phd', 'undergrad', or 'none'
        academic_calendar: Calendar configuration
    
    Returns:
        float: Multiplier for hours (0.3 to 1.5)
    """
    if calendar_type == 'phd':
        # PhD students: only affected by summer
        week_str = get_week_label(week_start)
        summer = academic_calendar.get('summer_2025', {})
        if summer.get('start', '') <= week_str <= summer.get('end', ''):
            return 1.2  # Slight summer boost
        return 1.0  # Consistent year-round
    
    elif calendar_type == 'undergrad':
        week_str = get_week_label(week_start)
        
        # Check all semesters
        for semester_name in ['fall_2024', 'winter_2025', 'summer_2025', 'fall_2025']:
            semester = academic_calendar.get(semester_name, {})
            
            # Exam period (highest priority)
            exam = semester.get('exam_period', {})
            if exam.get('start', '') <= week_str <= exam.get('end', ''):
                return exam.get('multiplier', 0.3)
            
            # Study week
            study = semester.get('study_week', {})
            if study.get('start', '') <= week_str <= study.get('end', ''):
                return study.get('multiplier', 0.5)
            
            # Reading week
            reading = semester.get('reading_week', {})
            if reading.get('start', '') <= week_str <= reading.get('end', ''):
                return reading.get('multiplier', 1.5)
        
        # Summer term
        summer = academic_calendar.get('summer_2025', {})
        if summer.get('start', '') <= week_str <= summer.get('end', ''):
            return summer.get('multiplier', 1.3)
        
        # Default: normal semester
        return 1.0
    
    else:  # 'none' or quit
        return 0

def sample_weekly_hours(role, week_modifier=1.0):
    """
    Sample hours for a user based on role and week modifier.
    Capped by role's max_hours (TD 15h, Lead 13h, Member 10h).
    """
    config = ROLE_DISTRIBUTIONS.get(role, ROLE_DISTRIBUTIONS['member'])
    max_h = config.get('max_hours', 10.0)
    
    base_hours = random.gauss(config['mean'], config['std_dev'])
    adjusted_hours = base_hours * week_modifier
    final_hours = max(0, min(max_h, adjusted_hours))
    return round(final_hours, 1)

def get_available_weeks(tasks, weeks_historical=20, weeks_lookahead=4):
    """Get list of weeks covered by tasks."""
    if not tasks:
        return []
    
    # Find date range from tasks
    dates = []
    for task in tasks:
        if task.get('start_date'):
            dates.append(datetime.fromisoformat(task['start_date'].replace('Z', '+00:00')))
        if task.get('end_date'):
            dates.append(datetime.fromisoformat(task['end_date'].replace('Z', '+00:00')))
    
    if not dates:
        return []
    
    min_date = min(dates)
    max_date = max(dates)
    
    # Add buffer
    start_date = min_date - timedelta(weeks=weeks_historical)
    end_date = max_date + timedelta(weeks=weeks_lookahead)
    
    # Generate weeks
    weeks = []
    current = get_week_start(start_date)
    end = get_week_start(end_date)
    
    while current <= end:
        weeks.append(current)
        current += timedelta(days=7)
    
    return weeks

def get_user_tasks_for_week(user_id, week_start, all_tasks):
    """
    Get tasks assigned to user that overlap with given week.
    Uses user_id (integer) to match against task resource type_id for reliable matching.
    
    Args:
        user_id: TeamGantt user ID (integer)
        week_start: Monday of the week (date)
        all_tasks: List of all tasks (from API, with resources)
    
    Returns:
        List of tasks assigned to user in this week
    """
    week_end = week_start + timedelta(days=6)  # Sunday
    
    user_tasks = []
    for task in all_tasks:
        # Match by user_id against resource type_id (exact integer match)
        resources = task.get('resources', [])
        if not any(r.get('type_id') == user_id for r in resources if isinstance(r, dict)):
            continue
        
        # Check if task overlaps with week
        try:
            task_start = datetime.fromisoformat(task.get('start_date', '').replace('Z', '+00:00')).date()
            task_end = datetime.fromisoformat(task.get('end_date', '').replace('Z', '+00:00')).date()
            
            # Task overlaps if: task_start <= week_end AND task_end >= week_start
            if task_start <= week_end and task_end >= week_start:
                user_tasks.append(task)
        except:
            continue
    
    return user_tasks

def calculate_duration_days(task):
    """Calculate task duration in days."""
    try:
        start = datetime.fromisoformat(task.get('start_date', '').replace('Z', '+00:00'))
        end = datetime.fromisoformat(task.get('end_date', '').replace('Z', '+00:00'))
        return max(1, (end - start).days)
    except:
        return 5  # Default 5 days if dates missing

def load_task_estimates():
    """
    Load task estimates from local file.
    Run analyze_tasks.py first to generate this file.
    
    Returns:
        dict: {task_id: estimated_hours}
    """
    estimates_file = Path(__file__).parent / 'task_estimates.json'
    
    if not estimates_file.exists():
        print("❌ ERROR: task_estimates.json not found")
        print()
        print("Run this first to analyze tasks and create estimates:")
        print("  python3 analyze_tasks.py")
        print()
        sys.exit(1)
    
    try:
        with open(estimates_file) as f:
            data = json.load(f)
        
        # Extract task_id -> estimated_hours mapping
        estimates = {}
        for task_id, task_data in data.get('tasks', {}).items():
            estimates[int(task_id)] = task_data.get('estimated_hours', 5.0)
        
        return estimates
    except Exception as e:
        print(f"❌ ERROR loading task_estimates.json: {e}")
        sys.exit(1)

def estimate_task_hours(task, task_estimates_lookup):
    """
    Get estimated hours for a task from pre-analyzed estimates.
    
    Args:
        task: Task dict
        task_estimates_lookup: Dict of {task_id: estimated_hours}
    
    Returns:
        float: Estimated hours needed
    """
    task_id = task['id']
    
    # Look up in pre-analyzed estimates
    estimated = task_estimates_lookup.get(task_id, 5.0)
    
    return estimated

def calculate_task_weights(tasks, task_estimates_lookup):
    """
    Calculate how to distribute hours across tasks based on task size/complexity.
    Uses pre-analyzed estimates from task_estimates.json.
    Bigger tasks get proportionally more hours.
    
    Args:
        tasks: List of tasks
        task_estimates_lookup: Dict of {task_id: estimated_hours}
    
    Returns:
        Dict mapping task_id to weight (0-1, sums to 1.0)
    """
    if not tasks:
        return {}
    
    # Get estimate for each task
    task_estimates = {}
    for task in tasks:
        estimated = estimate_task_hours(task, task_estimates_lookup)
        task_estimates[task['id']] = estimated
    
    # Calculate total estimated hours
    total_estimated = sum(task_estimates.values())
    
    if total_estimated == 0:
        # Fallback to equal weights if all estimates are 0
        weight = 1.0 / len(tasks)
        return {task['id']: weight for task in tasks}
    
    # Calculate proportional weights
    weights = {
        task_id: estimate / total_estimated
        for task_id, estimate in task_estimates.items()
    }
    
    return weights

def distribute_hours_into_time_blocks(task_id, task_name, total_hours, week_start, user_name, user_id=None):
    """
    Create 1 time block per task per week (single entry with weekly total).
    Uses Monday 9am as the entry date; hours represent the full week.
    """
    if total_hours <= 0:
        return []
    
    total_hours = round(total_hours, 1)
    if total_hours < 0.5:
        return []
    
    # Single block: Monday 9am, duration = total_hours
    start_time = datetime.combine(week_start, datetime.min.time()).replace(hour=9, minute=0, second=0)
    end_time = start_time + timedelta(hours=total_hours)
    
    return [{
        'task_id': task_id,
        'task_name': task_name,
        'user_name': user_name,
        'user_id': user_id,
        'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'hours': total_hours,
        'date': week_start.strftime('%Y-%m-%d')
    }]

def create_or_get_overhead_task(td_name, branch_name, all_tasks):
    """
    Create or get TD overhead task.
    
    Args:
        td_name: TD's name
        branch_name: Branch name
        all_tasks: List of all tasks
    
    Returns:
        Task dict (either existing or new)
    """
    overhead_task_name = f"{branch_name} - TD Coordination & Oversight"
    
    # Check if task already exists
    for task in all_tasks:
        if task.get('name') == overhead_task_name:
            return task
    
    # Return a virtual task for dry run
    return {
        'id': f"overhead_{td_name}",
        'name': overhead_task_name,
        'type': 'task',
        'description': 'Cross-team coordination, technical reviews, integration work',
        'is_virtual': True  # Flag for dry run
    }

# ============================================================================
# MAIN LOGIC
# ============================================================================

def main():
    print("=" * 80)
    print("TeamGantt Actual Hours Population - Role-Based with Academic Calendar")
    print("=" * 80)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Mode: {'DRY RUN (preview only)' if DRY_RUN else 'LIVE EXECUTION'}")
    print()
    
    # Load configurations
    print("Loading configurations...")
    user_roles = load_json_config('user_roles.json')
    academic_calendar = load_json_config('academic_calendar.json')
    
    role_mapping = user_roles.get('role_mapping', {})
    branch_mapping = user_roles.get('branch_mapping', {})
    quit_users = user_roles.get('quit_users', [])
    
    print(f"  ✓ {len(role_mapping)} users configured")
    print(f"  ✓ {len(branch_mapping)} branches configured")
    print()
    
    # Fetch fresh data from TeamGantt API
    print("Fetching data from TeamGantt API...")
    all_tasks, user_id_map, tg_display_names = fetch_project_data()
    print()
    
    # Get available weeks from task date ranges
    weeks = get_available_weeks(all_tasks, weeks_historical=0, weeks_lookahead=4)
    print(f"  ✓ Processing {len(weeks)} weeks ({get_week_label(weeks[0])} to {get_week_label(weeks[-1])})")
    print()
    
    # Load task estimates
    print("Loading task estimates...")
    task_estimates_lookup = load_task_estimates()
    print(f"  ✓ Loaded estimates for {len(task_estimates_lookup)} tasks")
    print()
    
    # Process each user week by week
    all_time_blocks = []
    user_summaries = defaultdict(lambda: {'total_hours': 0, 'weeks_active': 0, 'role': '', 'overhead_hours': 0, 'task_count': 0})
    skipped_no_id = []
    
    print("Sampling hours for each user by week...")
    print()
    
    # Also auto-discover any TG users NOT in role_mapping and add them as members
    for person_name, uid in user_id_map.items():
        if person_name not in role_mapping:
            # Skip the PM account
            display = tg_display_names.get(uid, '')
            if 'aUToronto PM' in display or 'PM' == person_name:
                continue
            # Auto-detect role from display name
            if '- TD' in display:
                auto_role = 'td'
            elif '- LEAD' in display or '- LEAAD' in display:
                auto_role = 'lead'
            else:
                auto_role = 'member'
            role_mapping[person_name] = auto_role
            print(f"  Auto-added: {person_name} as {auto_role} (TG: {display})")
    
    print(f"  ✓ Final user count: {len(role_mapping)}")
    print()
    
    for user_name, role in role_mapping.items():
        # Resolve TeamGantt user_id
        user_id = user_id_map.get(user_name)
        
        # Check if quit
        if role == 'quit' or user_name in quit_users:
            user_summaries[user_name] = {'total_hours': 0, 'weeks_active': 0, 'role': role,
                                          'overhead_hours': 0, 'task_count': 0, 'avg_per_week': 0, 'user_id': None}
            continue
        
        if not user_id:
            skipped_no_id.append(user_name)
            user_summaries[user_name] = {'total_hours': 0, 'weeks_active': 0, 'role': role,
                                          'overhead_hours': 0, 'task_count': 0, 'avg_per_week': 0, 'user_id': None}
            continue
        
        role_config = ROLE_DISTRIBUTIONS.get(role, ROLE_DISTRIBUTIONS['member'])
        calendar_type = role_config['calendar_type']
        is_td = role == 'td'
        overhead_pct = role_config.get('overhead_percentage', 0)
        
        user_total_hours = 0
        user_weeks_active = 0
        user_overhead_hours = 0
        user_task_ids = set()
        
        for week_start in weeks:
            # Get week modifier
            week_modifier = get_week_modifier(week_start, calendar_type, academic_calendar)
            
            # Sample total hours for this week
            total_week_hours = sample_weekly_hours(role, week_modifier)
            
            if total_week_hours < 0.5:
                continue  # Skip weeks with negligible hours
            
            # Get user's tasks for this week (match by user_id, not name)
            user_tasks = get_user_tasks_for_week(user_id, week_start, all_tasks)
            
            # Handle TD overhead - DISABLED FOR NOW
            overhead_hours = 0
            task_hours_pool = total_week_hours
            
            # if is_td and total_week_hours > 0:
            #     overhead_hours = total_week_hours * overhead_pct
            #     task_hours_pool = total_week_hours * (1 - overhead_pct)
            #     
            #     # Get or create overhead task
            #     branch = next((b for b, td in branch_mapping.items() if td == user_name), user_name)
            #     overhead_task = create_or_get_overhead_task(user_name, branch, all_tasks)
            #     
            #     # Create time blocks for overhead
            #     overhead_blocks = distribute_hours_into_time_blocks(
            #         overhead_task['id'],
            #         overhead_task['name'],
            #         overhead_hours,
            #         week_start,
            #         user_name
            #     )
            #     all_time_blocks.extend(overhead_blocks)
            #     user_overhead_hours += overhead_hours
            
            # Distribute remaining hours across tasks
            if user_tasks and task_hours_pool > 0:
                task_weights = calculate_task_weights(user_tasks, task_estimates_lookup)
                
                for task in user_tasks:
                    task_hours = task_hours_pool * task_weights[task['id']]
                    user_task_ids.add(task['id'])
                    
                    if task_hours >= 0.5:
                        time_blocks = distribute_hours_into_time_blocks(
                            task['id'],
                            task['name'],
                            task_hours,
                            week_start,
                            user_name,
                            user_id=user_id
                        )
                        all_time_blocks.extend(time_blocks)
            
            user_total_hours += total_week_hours
            user_weeks_active += 1
        
        # Store summary
        user_summaries[user_name] = {
            'total_hours': user_total_hours,
            'weeks_active': user_weeks_active,
            'role': role,
            'overhead_hours': user_overhead_hours,
            'task_count': len(user_task_ids),
            'avg_per_week': user_total_hours / user_weeks_active if user_weeks_active > 0 else 0,
            'user_id': user_id,
            'time_blocks': len([b for b in all_time_blocks if b.get('user_id') == user_id])
        }
    
    # Display summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    if skipped_no_id:
        print(f"⚠️  Skipped {len(skipped_no_id)} users (no TeamGantt ID): {', '.join(skipped_no_id)}")
        print()
    
    print(f"{'User':<28} {'Role':<8} {'TG ID':<12} {'Hours':<9} {'Tasks':<7} {'Blocks':<8} {'Wks':<5} {'Avg/Wk':<8}")
    print("-" * 95)
    
    active_users = 0
    users_with_blocks = 0
    for user_name in sorted(user_summaries.keys(), key=lambda u: user_summaries[u]['total_hours'], reverse=True):
        summary = user_summaries[user_name]
        uid_str = str(summary.get('user_id', '')) if summary.get('user_id') else 'N/A'
        blocks = summary.get('time_blocks', 0)
        print(f"{user_name:<28} {summary['role']:<8} {uid_str:<12} {summary['total_hours']:>7.1f}h "
              f"{summary.get('task_count', 0):>5} {blocks:>6} {summary['weeks_active']:>4} {summary['avg_per_week']:>6.1f}h")
        if summary['total_hours'] > 0:
            active_users += 1
        if blocks > 0:
            users_with_blocks += 1
    
    total_hours = sum(s['total_hours'] for s in user_summaries.values())
    total_blocks = len(all_time_blocks)
    blocked_hours = sum(b['hours'] for b in all_time_blocks)
    
    print()
    print(f"Active users: {active_users}/{len(role_mapping)} ({users_with_blocks} with time blocks)")
    print(f"Total time blocks: {total_blocks}")
    print(f"Total sampled hours: {total_hours:.1f}h")
    print(f"Total hours in time blocks: {blocked_hours:.1f}h")
    print(f"Hours coverage: {blocked_hours/total_hours*100:.1f}% of sampled hours have task assignments")
    print()
    
    # Show sample time blocks
    print("Sample time blocks (first 10):")
    print(f"{'User':<20} {'Task':<35} {'Date':<12} {'Hours':<6}")
    print("-" * 80)
    for block in all_time_blocks[:10]:
        print(f"{block['user_name']:<20} {block['task_name'][:33]:<35} "
              f"{block['date']:<12} {block['hours']:>5.1f}h")
    
    if len(all_time_blocks) > 10:
        print(f"... and {len(all_time_blocks) - 10} more time blocks")
    
    # Show example of task weighting
    print()
    print("=" * 80)
    print("TASK WEIGHTING EXAMPLE")
    print("=" * 80)
    print()
    print("Hours are distributed based on task size/complexity:")
    print("  - Uses estimated_hours from TeamGantt if available")
    print("  - Falls back to duration × 2h/day if no estimate")
    print("  - Bigger tasks get proportionally more hours")
    print()
    print("Example:")
    print("  User has 10h this week, 3 tasks assigned:")
    print("    • Task A: 20h estimated → 44% weight → 4.4h this week")
    print("    • Task B: 15h estimated → 33% weight → 3.3h this week")
    print("    • Task C: 10h estimated → 22% weight → 2.2h this week")
    print("  Total: 10h (matches user's weekly allocation)")
    print()
    
    print()
    print("=" * 80)
    
    if DRY_RUN:
        print()
        print("✅ DRY RUN COMPLETE - No changes were made")
        print()
        print("To execute these changes:")
        print("1. Review the preview above")
        print("2. Update user_roles.json with actual team member names")
        print("3. Edit this script and set DRY_RUN = False")
        print("4. Run the script again")
        
        # Save plan to file (ALL blocks, not truncated)
        plan_file = '/tmp/actual_hours_population_plan.json'
        with open(plan_file, 'w') as f:
            json.dump({
                'user_summaries': dict(user_summaries),
                'time_blocks': all_time_blocks,
                'total_blocks': len(all_time_blocks),
                'skipped_no_id': skipped_no_id
            }, f, indent=2)
        print()
        print(f"💾 Detailed plan saved to: {plan_file}")
    else:
        print()
        print("🚀 EXECUTING UPDATES...")
        print("=" * 80)
        print()
        print("Creating time entries in TeamGantt...")
        
        success_count = 0
        fail_count = 0
        
        for i, block in enumerate(all_time_blocks, 1):
            task_id = str(block.get('task_id', ''))
            if task_id.startswith('overhead_'):
                print(f"  [{i}/{len(all_time_blocks)}] Skipping virtual overhead task")
                continue
            
            print(f"  [{i}/{len(all_time_blocks)}] {block['user_name'][:20]} - "
                  f"{block['task_name'][:30]} ({block['hours']:.1f}h)...", end=' ')
            
            # Execute POST request (with user_id to log under correct user)
            payload = {
                'task_id': block['task_id'],
                'start_time': block['start_time'],
                'end_time': block['end_time']
            }
            if block.get('user_id'):
                payload['user_id'] = block['user_id']
            
            cmd = [
                'curl', '-s', '-X', 'POST',
                '-H', f'Authorization: Bearer {API_TOKEN}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps(payload),
                f'{API_BASE}/times'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    if response.get('id'):
                        print("✅")
                        success_count += 1
                    else:
                        print("⚠️")
                        fail_count += 1
                else:
                    print("❌")
                    fail_count += 1
            except Exception as e:
                print(f"❌ ({str(e)[:20]})")
                fail_count += 1
            
            time.sleep(RATE_LIMIT_DELAY)
        
        print()
        print("=" * 80)
        print("✅ EXECUTION COMPLETE!")
        print()
        print(f"Summary:")
        print(f"  • Time blocks created: {success_count}/{len(all_time_blocks)}")
        print(f"  • Failed: {fail_count}")
        print(f"  • Total hours logged: {sum(b['hours'] for b in all_time_blocks):.1f}h")
        print()
        print(f"Verify in TeamGantt: https://app.teamgantt.com/projects/{PROJECT_ID}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
