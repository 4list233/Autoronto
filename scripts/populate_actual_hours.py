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
import numpy as np
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
API_TOKEN = os.getenv('TEAMGANTT_API_KEY', '')
PROJECT_ID = int(os.getenv('TEAMGANTT_PROJECT_ID', '0'))
API_BASE = "https://api.teamgantt.com/v1"
DRY_RUN = True  # Set to False to actually execute
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

# Validate configuration
if not API_TOKEN:
    print("❌ ERROR: TEAMGANTT_API_KEY not found")
    print("Please create a .env file with: TEAMGANTT_API_KEY=your_token_here")
    sys.exit(1)

if not PROJECT_ID:
    print("❌ ERROR: TEAMGANTT_PROJECT_ID not found")
    sys.exit(1)

# Role-based distributions (hours per week)
ROLE_DISTRIBUTIONS = {
    'chad_phd': {
        'mean': 12.0,
        'std_dev': 1.5,
        'calendar_type': 'phd',  # Not affected by undergrad calendar
        'description': 'PhD student - 9-15h/week year-round'
    },
    'td': {
        'mean': 12.0,
        'std_dev': 1.5,
        'calendar_type': 'undergrad',
        'overhead_percentage': 0.375,  # 37.5% for coordination
        'description': 'Technical Director - 9-15h/week + overhead'
    },
    'lead': {
        'mean': 10.5,
        'std_dev': 1.25,
        'calendar_type': 'undergrad',
        'description': 'Team lead - 8-13h/week'
    },
    'member': {
        'mean': 8.5,
        'std_dev': 0.75,
        'calendar_type': 'undergrad',
        'description': 'Regular member - 7-10h/week'
    },
    'inactive': {
        'mean': 3.0,
        'std_dev': 1.5,
        'calendar_type': 'undergrad',
        'description': 'Inactive/struggling - 0-6h/week'
    },
    'quit': {
        'mean': 0,
        'std_dev': 0,
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
    
    Args:
        role: User role ('chad_phd', 'td', 'lead', 'member', etc.)
        week_modifier: Calendar multiplier (0.3 to 1.5)
    
    Returns:
        float: Hours for the week (rounded to 1 decimal)
    """
    config = ROLE_DISTRIBUTIONS.get(role, ROLE_DISTRIBUTIONS['member'])
    
    # Sample from normal distribution
    base_hours = np.random.normal(config['mean'], config['std_dev'])
    
    # Apply week modifier
    adjusted_hours = base_hours * week_modifier
    
    # Clamp to realistic bounds
    final_hours = np.clip(adjusted_hours, 0, 25)
    
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

def get_user_tasks_for_week(user_name, week_start, all_tasks):
    """
    Get tasks assigned to user that overlap with given week.
    
    Args:
        user_name: User's name
        week_start: Monday of the week
        all_tasks: List of all tasks
    
    Returns:
        List of tasks assigned to user in this week
    """
    week_end = week_start + timedelta(days=6)  # Sunday
    
    user_tasks = []
    for task in all_tasks:
        # Check if user is assigned
        resources = task.get('resources', [])
        if not any(r.get('name') == user_name for r in resources):
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

def distribute_hours_into_time_blocks(task_id, task_name, total_hours, week_start, user_name):
    """
    Distribute hours into realistic time blocks across the week.
    
    Args:
        task_id: Task ID
        task_name: Task name
        total_hours: Total hours to distribute
        week_start: Monday of the week
        user_name: User name
    
    Returns:
        List of time block specifications
    """
    if total_hours <= 0:
        return []
    
    time_blocks = []
    hours_remaining = total_hours
    
    # Distribute across weekdays (Mon-Fri)
    days_available = 5
    daily_hours_target = total_hours / days_available
    
    # Limit to reasonable daily hours (2-8h)
    if daily_hours_target > 8:
        days_available = max(5, int(np.ceil(total_hours / 6)))
    
    current_day = week_start
    days_used = 0
    
    while hours_remaining > 0.5 and days_used < days_available:
        # Skip weekends
        if current_day.weekday() >= 5:
            current_day += timedelta(days=1)
            continue
        
        # Allocate hours for this day (2-8h, with some variance)
        daily_hours = min(
            hours_remaining,
            max(0.5, np.random.uniform(2, min(8, total_hours / 2)))
        )
        daily_hours = round(daily_hours, 1)
        
        if daily_hours >= 0.5:
            # Create time block (9am-5pm window)
            start_hour = np.random.randint(9, 15)
            start_time = datetime.combine(current_day, datetime.min.time()).replace(hour=start_hour)
            end_time = start_time + timedelta(hours=daily_hours)
            
            time_blocks.append({
                'task_id': task_id,
                'task_name': task_name,
                'user_name': user_name,
                'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'hours': daily_hours,
                'date': current_day.strftime('%Y-%m-%d')
            })
            
            hours_remaining -= daily_hours
        
        current_day += timedelta(days=1)
        days_used += 1
    
    return time_blocks

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
    
    # Load tasks
    print("Loading tasks from /tmp/test_project_tasks.json...")
    try:
        with open('/tmp/test_project_tasks.json') as f:
            all_tasks = json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: Task file not found")
        print("Run: cp ../data/children_flat_<PROJECT_ID>.json /tmp/test_project_tasks.json")
        return 1
    
    # Filter to only tasks
    all_tasks = [t for t in all_tasks if t.get('type') == 'task']
    print(f"  ✓ Loaded {len(all_tasks)} tasks")
    print()
    
    # Get available weeks
    weeks = get_available_weeks(all_tasks, weeks_historical=20, weeks_lookahead=4)
    print(f"  ✓ Processing {len(weeks)} weeks ({get_week_label(weeks[0])} to {get_week_label(weeks[-1])})")
    print()
    
    # Load task estimates
    print("Loading task estimates...")
    task_estimates_lookup = load_task_estimates()
    print(f"  ✓ Loaded estimates for {len(task_estimates_lookup)} tasks")
    print()
    
    # Process each user week by week
    all_time_blocks = []
    user_summaries = defaultdict(lambda: {'total_hours': 0, 'weeks_active': 0, 'role': '', 'overhead_hours': 0})
    
    print("Sampling hours for each user by week...")
    print()
    
    for user_name, role in role_mapping.items():
        print(f"User: {user_name} (Role: {role})")
        
        # Check if quit
        if user_name in quit_users:
            print(f"  ⏭️  Skipped (marked as quit)")
            print()
            continue
        
        role_config = ROLE_DISTRIBUTIONS.get(role, ROLE_DISTRIBUTIONS['member'])
        calendar_type = role_config['calendar_type']
        is_td = role == 'td'
        overhead_pct = role_config.get('overhead_percentage', 0)
        
        user_total_hours = 0
        user_weeks_active = 0
        user_overhead_hours = 0
        
        for week_start in weeks:
            # Get week modifier
            week_modifier = get_week_modifier(week_start, calendar_type, academic_calendar)
            
            # Sample total hours for this week
            total_week_hours = sample_weekly_hours(role, week_modifier)
            
            if total_week_hours < 0.5:
                continue  # Skip weeks with negligible hours
            
            # Get user's tasks for this week
            user_tasks = get_user_tasks_for_week(user_name, week_start, all_tasks)
            
            # Handle TD overhead
            overhead_hours = 0
            task_hours_pool = total_week_hours
            
            if is_td and total_week_hours > 0:
                overhead_hours = total_week_hours * overhead_pct
                task_hours_pool = total_week_hours * (1 - overhead_pct)
                
                # Get or create overhead task
                branch = next((b for b, td in branch_mapping.items() if td == user_name), user_name)
                overhead_task = create_or_get_overhead_task(user_name, branch, all_tasks)
                
                # Create time blocks for overhead
                overhead_blocks = distribute_hours_into_time_blocks(
                    overhead_task['id'],
                    overhead_task['name'],
                    overhead_hours,
                    week_start,
                    user_name
                )
                all_time_blocks.extend(overhead_blocks)
                user_overhead_hours += overhead_hours
            
            # Distribute remaining hours across tasks
            if user_tasks and task_hours_pool > 0:
                task_weights = calculate_task_weights(user_tasks, task_estimates_lookup)
                
                for task in user_tasks:
                    task_hours = task_hours_pool * task_weights[task['id']]
                    
                    if task_hours >= 0.5:
                        time_blocks = distribute_hours_into_time_blocks(
                            task['id'],
                            task['name'],
                            task_hours,
                            week_start,
                            user_name
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
            'avg_per_week': user_total_hours / user_weeks_active if user_weeks_active > 0 else 0
        }
        
        print(f"  ✓ {user_weeks_active} weeks active, {user_total_hours:.1f}h total")
        if user_overhead_hours > 0:
            print(f"    ├─ Overhead: {user_overhead_hours:.1f}h ({overhead_pct*100:.1f}%)")
            print(f"    └─ Tasks: {user_total_hours - user_overhead_hours:.1f}h")
        print()
    
    # Display summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"{'User':<25} {'Role':<12} {'Total Hours':<12} {'Weeks':<8} {'Avg/Week':<10}")
    print("-" * 80)
    
    for user_name in sorted(user_summaries.keys(), key=lambda u: user_summaries[u]['total_hours'], reverse=True):
        summary = user_summaries[user_name]
        print(f"{user_name:<25} {summary['role']:<12} {summary['total_hours']:>10.1f}h "
              f"{summary['weeks_active']:>6} {summary['avg_per_week']:>8.1f}h")
    
    print()
    print(f"Total time blocks: {len(all_time_blocks)}")
    print(f"Total project hours: {sum(s['total_hours'] for s in user_summaries.values()):.1f}h")
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
        
        # Save plan to file
        plan_file = '/tmp/actual_hours_population_plan.json'
        with open(plan_file, 'w') as f:
            json.dump({
                'user_summaries': dict(user_summaries),
                'time_blocks': all_time_blocks[:100],  # Sample
                'total_blocks': len(all_time_blocks)
            }, f, indent=2)
        print(f()
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
            if block.get('task_id', '').startswith('overhead_'):
                print(f"  [{i}/{len(all_time_blocks)}] Skipping virtual overhead task")
                continue
            
            print(f"  [{i}/{len(all_time_blocks)}] {block['user_name'][:20]} - "
                  f"{block['task_name'][:30]} ({block['hours']:.1f}h)...", end=' ')
            
            # Execute POST request
            cmd = [
                'curl', '-s', '-X', 'POST',
                '-H', f'Authorization: Bearer {API_TOKEN}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'task_id': block['task_id'],
                    'start_time': block['start_time'],
                    'end_time': block['end_time']
                }),
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
