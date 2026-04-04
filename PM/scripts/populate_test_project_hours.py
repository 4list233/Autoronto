#!/usr/bin/env python3
"""
Populate estimated and actual hours for TeamGantt test project
Option A: Realistic Scenario
- Estimate based on task characteristics
- Only add actuals for tasks with progress > 0
- Natural variance in time entries
- Respects task start dates (no future work)
"""

import json
import random
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import time
import subprocess
from pathlib import Path

# Load environment variables from .env file
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

# Configuration - Read from environment variables
API_TOKEN = os.getenv('TEAMGANTT_API_KEY', '')
PROJECT_ID = int(os.getenv('TEAMGANTT_PROJECT_ID', '0'))
API_BASE = "https://api.teamgantt.com/v1"
DRY_RUN = True  # Set to False to actually execute (SAFER DEFAULT)
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

# Validate configuration
if not API_TOKEN:
    print("❌ ERROR: TEAMGANTT_API_KEY not found in environment or .env file")
    print("Please create a .env file with: TEAMGANTT_API_KEY=your_token_here")
    sys.exit(1)

if not PROJECT_ID:
    print("❌ ERROR: TEAMGANTT_PROJECT_ID not found in environment or .env file")
    print("Please create a .env file with: TEAMGANTT_PROJECT_ID=your_project_id")
    sys.exit(1)

# Estimation rules based on task keywords
ESTIMATION_RULES = {
    'form': (0.5, 1),           # Forms/admin
    'proposal': (8, 12),         # Major deliverables
    'report': (15, 25),          # Reports
    'presentation': (5, 8),      # Presentations
    'meeting': (1, 2),           # Meetings
    'review': (2, 4),            # Reviews
    'research': (8, 15),         # Research
    'design': (5, 10),           # Design work
    'implementation': (10, 20),  # Implementation
    'testing': (5, 10),          # Testing
    'documentation': (3, 6),     # Documentation
    'planning': (3, 5),          # Planning
    'milestone': (0.5, 1),       # Milestone coordination
}

DEFAULT_ESTIMATE = (3, 8)  # Default range if no keywords match


def estimate_hours(task: Dict) -> float:
    """Estimate hours for a task based on its characteristics."""
    name = task.get('name', '').lower()
    task_type = task.get('type', '')
    
    # Milestones get minimal estimates
    if task_type == 'milestone':
        return round(random.uniform(0.5, 1.0), 1)
    
    # Check for keywords
    for keyword, (min_hours, max_hours) in ESTIMATION_RULES.items():
        if keyword in name:
            # Add variance based on task duration
            duration_days = calculate_duration_days(task)
            multiplier = 1.0 + (duration_days / 100)  # Longer tasks = more hours
            
            estimated = random.uniform(min_hours, max_hours) * multiplier
            return round(estimated, 1)
    
    # Default estimate
    min_hours, max_hours = DEFAULT_ESTIMATE
    return round(random.uniform(min_hours, max_hours), 1)


def calculate_duration_days(task: Dict) -> int:
    """Calculate task duration in days."""
    try:
        start = datetime.fromisoformat(task.get('start_date', '').replace('Z', '+00:00'))
        end = datetime.fromisoformat(task.get('end_date', '').replace('Z', '+00:00'))
        return max(1, (end - start).days)
    except:
        return 1


def calculate_actual_hours(estimated: float, progress: int) -> float:
    """Calculate actual hours based on progress with realistic variance."""
    if progress == 0:
        return 0
    
    base_actual = estimated * (progress / 100.0)
    # Add natural variance: some tasks go faster, some slower
    variance = random.uniform(0.85, 1.15)
    return round(base_actual * variance, 1)


def distribute_hours_into_time_blocks(
    task_id: int,
    task_name: str,
    total_hours: float,
    start_date: str,
    end_date: str
) -> List[Dict]:
    """
    Distribute total hours into realistic time blocks across working days.
    Returns list of time block specifications (start_time, end_time).
    """
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        today = datetime.now()
        
        # Don't create time blocks in the future
        latest_date = min(today, datetime.fromisoformat(end_date.replace('Z', '+00:00')))
        
        # Get working days (Mon-Fri) between start and latest_date
        working_days = []
        current = start
        while current <= latest_date:
            if current.weekday() < 5:  # Mon-Fri
                working_days.append(current.date())
            current += timedelta(days=1)
        
        if not working_days or total_hours <= 0:
            return []
        
        # Distribute hours across days
        time_blocks = []
        hours_remaining = total_hours
        
        # Front-load work (more realistic for partially complete tasks)
        num_days = min(len(working_days), max(1, int(total_hours / 4) + 1))
        selected_days = working_days[:num_days]
        
        for i, day in enumerate(selected_days):
            if hours_remaining <= 0:
                break
            
            # Allocate 2-6 hours per day with diminishing amounts
            daily_hours = min(
                hours_remaining,
                random.uniform(2, 6) * (1 - i / (num_days * 2))  # Front-load
            )
            daily_hours = round(daily_hours, 1)
            
            if daily_hours < 0.5:
                continue
            
            # Create time block (9am-5pm window)
            start_hour = random.randint(9, 14)
            start_time = datetime.combine(day, datetime.min.time()).replace(
                hour=start_hour, tzinfo=None
            )
            end_time = start_time + timedelta(hours=daily_hours)
            
            time_blocks.append({
                'task_id': task_id,
                'task_name': task_name,
                'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'hours': daily_hours
            })
            
            hours_remaining -= daily_hours
        
        return time_blocks
    
    except Exception as e:
        print(f"Error distributing hours for task {task_id}: {e}")
        return []


def main():
    print("=" * 80)
    print("TeamGantt Test Project - Time Population Script (Option A: Realistic)")
    print("=" * 80)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Mode: {'DRY RUN (preview only)' if DRY_RUN else 'LIVE EXECUTION'}")
    print()
    
    # Load tasks
    print("Loading tasks from /tmp/test_project_tasks.json...")
    try:
        with open('/tmp/test_project_tasks.json') as f:
            all_items = json.load(f)
    except FileNotFoundError:
        print("ERROR: Task file not found. Run the fetch command first.")
        return 1
    
    # Filter to only tasks and milestones
    tasks = [t for t in all_items if t.get('type') in ['task', 'milestone']]
    print(f"Found {len(tasks)} tasks/milestones to process")
    print()
    
    # Generate estimates and actuals
    updates = []
    time_blocks_all = []
    
    for task in tasks:
        task_id = task['id']
        task_name = task.get('name', 'Unknown')
        task_type = task.get('type', 'task')
        progress = task.get('percent_complete', 0)
        current_estimate = task.get('estimated_hours', 0)
        current_actual = task.get('actual_hours', 0)
        resources = task.get('resources', [])
        
        # Skip if already has estimates (optional - remove this to recalculate)
        if current_estimate > 0:
            print(f"⏭️  Skipping {task_name} (already has {current_estimate}h estimated)")
            continue
        
        # Calculate new estimate
        estimated_hours = estimate_hours(task)
        
        # Calculate actual hours only if task has progress
        actual_hours = 0
        time_blocks = []
        if progress > 0:
            actual_hours = calculate_actual_hours(estimated_hours, progress)
            
            # Distribute into time blocks
            if actual_hours > 0:
                time_blocks = distribute_hours_into_time_blocks(
                    task_id,
                    task_name,
                    actual_hours,
                    task.get('start_date', ''),
                    task.get('end_date', '')
                )
        
        updates.append({
            'task_id': task_id,
            'task_name': task_name,
            'task_type': task_type,
            'estimated_hours': estimated_hours,
            'actual_hours': actual_hours,
            'progress': progress,
            'time_blocks': len(time_blocks),
            'resources': len(resources)
        })
        
        time_blocks_all.extend(time_blocks)
    
    # Display summary
    print("\n" + "=" * 80)
    print("PREVIEW OF CHANGES")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"  Tasks to update: {len(updates)}")
    print(f"  Total estimated hours: {sum(u['estimated_hours'] for u in updates):.1f}h")
    print(f"  Total actual hours: {sum(u['actual_hours'] for u in updates):.1f}h")
    print(f"  Time blocks to create: {len(time_blocks_all)}")
    print()
    
    # Show sample updates
    print("📋 Sample updates (first 10):")
    print(f"{'Task Name':<40} {'Type':<10} {'Est.':<6} {'Actual':<7} {'Prog.':<6} {'Blocks':<7}")
    print("-" * 85)
    for u in updates[:10]:
        print(f"{u['task_name'][:38]:<40} {u['task_type']:<10} "
              f"{u['estimated_hours']:>5.1f}h {u['actual_hours']:>6.1f}h "
              f"{u['progress']:>4}% {u['time_blocks']:>6}")
    
    if len(updates) > 10:
        print(f"... and {len(updates) - 10} more tasks")
    
    # Show sample time blocks
    if time_blocks_all:
        print(f"\n⏱️  Sample time blocks (first 5):")
        for tb in time_blocks_all[:5]:
            print(f"  {tb['task_name'][:35]:<37} | {tb['start_time'][:10]} | {tb['hours']:.1f}h")
        if len(time_blocks_all) > 5:
            print(f"  ... and {len(time_blocks_all) - 5} more time blocks")
    
    print("\n" + "=" * 80)
    
    if DRY_RUN:
        print("\n✅ DRY RUN COMPLETE - No changes were made")
        print("\nTo execute these changes:")
        print("1. Review the preview above")
        print("2. Edit this script and set DRY_RUN = False")
        print("3. Run the script again")
        
        # Save plan to file
        plan_file = '/tmp/time_population_plan.json'
        with open(plan_file, 'w') as f:
            json.dump({
                'updates': updates,
                'time_blocks': time_blocks_all
            }, f, indent=2)
        print(f"\n💾 Detailed plan saved to: {plan_file}")
    else:
        print("\n🚀 EXECUTING UPDATES...")
        print("=" * 80)
        
        # Phase 1: Update estimated hours
        print("\n📝 Phase 1: Updating estimated hours...")
        success_count = 0
        fail_count = 0
        
        for i, update in enumerate(updates, 1):
            task_id = update['task_id']
            estimated = update['estimated_hours']
            task_name = update['task_name']
            
            print(f"  [{i}/{len(updates)}] Updating {task_name[:40]:<42} -> {estimated:.1f}h...", end=' ')
            
            # Execute PATCH request
            cmd = [
                'curl', '-s', '-X', 'PATCH',
                '-H', f'Authorization: Bearer {API_TOKEN}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({'estimated_hours': estimated}),
                f'{API_BASE}/tasks/{task_id}'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    if response.get('estimated_hours') == estimated:
                        print("✅")
                        success_count += 1
                    else:
                        print(f"⚠️  (returned {response.get('estimated_hours')}h)")
                        success_count += 1
                else:
                    print(f"❌ (curl error)")
                    fail_count += 1
            except Exception as e:
                print(f"❌ ({str(e)[:30]})")
                fail_count += 1
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
        
        print(f"\n✅ Phase 1 complete: {success_count} updated, {fail_count} failed")
        
        # Phase 2: Create time blocks (if any)
        if time_blocks_all:
            print(f"\n⏱️  Phase 2: Creating {len(time_blocks_all)} time blocks...")
            block_success = 0
            block_fail = 0
            
            for i, block in enumerate(time_blocks_all, 1):
                print(f"  [{i}/{len(time_blocks_all)}] {block['task_name'][:35]:<37} {block['hours']:.1f}h...", end=' ')
                
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
                            block_success += 1
                        else:
                            print(f"⚠️")
                            block_fail += 1
                    else:
                        print(f"❌")
                        block_fail += 1
                except Exception as e:
                    print(f"❌ ({str(e)[:20]})")
                    block_fail += 1
                
                time.sleep(RATE_LIMIT_DELAY)
            
            print(f"\n✅ Phase 2 complete: {block_success} created, {block_fail} failed")
        else:
            print(f"\n⏭️  Phase 2: No time blocks to create (all tasks at 0% progress)")
        
        print("\n" + "=" * 80)
        print("✅ EXECUTION COMPLETE!")
        print(f"\nSummary:")
        print(f"  • Estimated hours updated: {success_count}/{len(updates)}")
        print(f"  • Time blocks created: {len(time_blocks_all)}")
        print(f"\nVerify in TeamGantt: https://app.teamgantt.com/projects/{PROJECT_ID}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
