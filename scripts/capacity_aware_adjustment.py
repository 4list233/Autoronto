#!/usr/bin/env python3
"""
Capacity-Aware Task Estimate Adjustment

Logic:
1. For each week in the project timeline
2. Find all active tasks for that week
3. Group tasks by assigned members
4. Calculate each member's available weekly hours (from role mapping)
5. Distribute their hours across concurrent tasks proportionally
6. Adjust task estimates to reflect realistic capacity constraints

This ensures that if a member has 3 tasks in the same week, the estimates
reflect that they're splitting their time, not working 40h on each task.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# File paths
SCRIPT_DIR = Path(__file__).parent
ESTIMATES_FILE = SCRIPT_DIR / "task_estimates.json"
USER_ROLES_FILE = SCRIPT_DIR / "user_roles.json"

# Role-based weekly hours (mean values from populate_actual_hours.py)
ROLE_WEEKLY_HOURS = {
    'chad_phd': 12.0,     # PhD student, high commitment
    'td': 11.0,           # Technical Director
    'lead': 9.0,          # Team Lead
    'member': 8.5,        # Regular member
    'inactive': 3.0,      # Low activity
    'quit': 0.0           # No hours
}

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def parse_date(date_str):
    """Parse date string to datetime"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def get_week_start(date):
    """Get Monday of the week for a given date"""
    return date - timedelta(days=date.weekday())

def get_weeks_between(start_date, end_date):
    """Get all Monday dates between start and end"""
    if not start_date or not end_date:
        return []
    
    weeks = []
    current = get_week_start(start_date)
    end = get_week_start(end_date)
    
    while current <= end:
        weeks.append(current)
        current += timedelta(days=7)
    
    return weeks

def extract_username(assigned_str):
    """Extract username from assignment string like '!Chad Paik' or 'MI - Forest Li - MEM'"""
    if not assigned_str:
        return None
    
    # Remove prefixes
    name = assigned_str.replace('!', '').replace('MI - ', '').strip()
    
    # Remove suffixes like ' - TD', ' - MEM', etc.
    if ' - ' in name:
        name = name.split(' - ')[0].strip()
    
    return name

def get_user_role(username, user_roles):
    """Get role for a user from user_roles mapping"""
    role_mapping = user_roles.get('role_mapping', {})
    
    # Direct match
    if username in role_mapping:
        return role_mapping[username]
    
    # Check if user is a branch lead
    for branch, lead_name in user_roles.get('branch_mapping', {}).items():
        if username == lead_name:
            return 'lead'
    
    # Check if user quit
    if username in user_roles.get('quit_users', []):
        return 'quit'
    
    # Default to member
    return 'member'

def get_user_weekly_hours(username, user_roles):
    """Get weekly hour capacity for a user"""
    role = get_user_role(username, user_roles)
    return ROLE_WEEKLY_HOURS.get(role, 8.5)

def analyze_concurrent_workload():
    """
    Main analysis function:
    1. Load all tasks and user roles
    2. For each week, find concurrent tasks per user
    3. Calculate realistic hour distribution
    4. Adjust task estimates based on capacity constraints
    """
    
    print("=" * 100)
    print("Capacity-Aware Task Estimate Adjustment")
    print("=" * 100)
    
    # Load data
    estimates_data = load_json(ESTIMATES_FILE)
    user_roles = load_json(USER_ROLES_FILE)
    
    tasks = estimates_data['tasks']
    
    # Build week-to-tasks mapping
    print("\n📅 Analyzing project timeline...")
    week_tasks = defaultdict(list)  # week -> [(task_id, task_data, assigned_users)]
    
    for task_id, task in tasks.items():
        if task['type'] == 'milestone' or task['estimated_hours'] == 0:
            continue
        
        start = parse_date(task.get('start_date'))
        end = parse_date(task.get('end_date'))
        
        if not start or not end:
            continue
        
        # Get assigned users
        assigned_users = []
        for assigned_str in task.get('assigned_to', []):
            username = extract_username(assigned_str)
            if username:
                assigned_users.append(username)
        
        # If no users assigned, skip capacity analysis for this task
        if not assigned_users:
            continue
        
        # Add to all weeks this task spans
        weeks = get_weeks_between(start, end)
        for week in weeks:
            week_str = week.strftime("%Y-%m-%d")
            week_tasks[week_str].append({
                'task_id': task_id,
                'task': task,
                'users': assigned_users
            })
    
    print(f"✓ Found {len(week_tasks)} weeks with active tasks")
    
    # Analyze concurrent workload per user per week
    print("\n👥 Analyzing concurrent workload...")
    
    user_week_workload = defaultdict(lambda: defaultdict(list))  # user -> week -> [tasks]
    
    for week_str, week_task_list in week_tasks.items():
        for item in week_task_list:
            for user in item['users']:
                user_week_workload[user][week_str].append(item)
    
    # Calculate capacity-adjusted estimates
    print("\n⚙️  Adjusting estimates based on capacity constraints...")
    
    adjustments = []
    
    for user, weeks in user_week_workload.items():
        weekly_capacity = get_user_weekly_hours(user, user_roles)
        
        for week_str, week_task_items in weeks.items():
            num_concurrent = len(week_task_items)
            
            if num_concurrent <= 1:
                continue  # No adjustment needed for single task
            
            # Calculate total estimate hours for all concurrent tasks
            total_estimated_hours = sum(item['task']['estimated_hours'] for item in week_task_items)
            
            # If total estimates exceed weekly capacity * number of weeks,
            # we need to adjust
            num_weeks = max(item['task']['duration_days'] / 7 for item in week_task_items)
            total_available_hours = weekly_capacity * num_weeks
            
            if total_estimated_hours > total_available_hours * 1.5:  # 50% buffer
                # Calculate adjustment factor
                adjustment_factor = (total_available_hours * 1.2) / total_estimated_hours
                
                for item in week_task_items:
                    task_id = item['task_id']
                    old_estimate = item['task']['estimated_hours']
                    new_estimate = round(old_estimate * adjustment_factor * 2) / 2  # Round to 0.5
                    new_estimate = max(2.0, new_estimate)  # Minimum 2h
                    
                    if abs(new_estimate - old_estimate) > 1.0:
                        adjustments.append({
                            'task_id': task_id,
                            'task_name': item['task']['name'],
                            'user': user,
                            'week': week_str,
                            'old': old_estimate,
                            'new': new_estimate,
                            'concurrent_tasks': num_concurrent,
                            'weekly_capacity': weekly_capacity
                        })
    
    # Apply adjustments
    print(f"\n✓ Found {len(adjustments)} tasks requiring capacity adjustment")
    
    # Group adjustments by task (take the most conservative adjustment)
    task_adjustments = {}
    for adj in adjustments:
        task_id = adj['task_id']
        if task_id not in task_adjustments or adj['new'] < task_adjustments[task_id]['new']:
            task_adjustments[task_id] = adj
    
    # Apply to estimates
    for task_id, adj in task_adjustments.items():
        tasks[task_id]['estimated_hours'] = adj['new']
        tasks[task_id]['source'] = 'capacity_adjusted'
    
    # Recalculate total
    total_hours = sum(task['estimated_hours'] for task in tasks.values())
    estimates_data['metadata']['total_estimated_hours'] = total_hours
    
    # Save
    save_json(ESTIMATES_FILE, estimates_data)
    
    print(f"\n{'=' * 100}")
    print("SAMPLE ADJUSTMENTS (showing 20 examples):")
    print(f"{'=' * 100}\n")
    
    for i, adj in enumerate(sorted(task_adjustments.values(), key=lambda x: x['old'] - x['new'], reverse=True)[:20], 1):
        print(f"{i}. {adj['task_name']}")
        print(f"   User: {adj['user']} (capacity: {adj['weekly_capacity']}h/week)")
        print(f"   {adj['old']}h → {adj['new']}h (reduced by {adj['old'] - adj['new']:.1f}h)")
        print(f"   Reason: {adj['concurrent_tasks']} concurrent tasks in week {adj['week']}")
        print(f"   Task ID: {adj['task_id']}")
        print()
    
    print(f"{'=' * 100}")
    print("SUMMARY:")
    print(f"  - Tasks adjusted: {len(task_adjustments)}")
    print(f"  - New total hours: {total_hours:.1f}h")
    print(f"{'=' * 100}")
    
    return task_adjustments

if __name__ == "__main__":
    try:
        analyze_concurrent_workload()
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("\nMake sure these files exist:")
        print(f"  - {ESTIMATES_FILE}")
        print(f"  - {USER_ROLES_FILE}")
        sys.exit(1)
