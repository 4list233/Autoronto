#!/usr/bin/env python3
"""
Randomly assign team members to tasks in the test project.
"""

import json
import os
import random
import subprocess
import time
import sys

# Configuration
# NOTE: Never hardcode API tokens in source control.
# Read from environment / .env instead.
API_TOKEN = os.getenv("TEAMGANTT_API_KEY", "")
PROJECT_ID = 4452374
API_BASE = "https://api.teamgantt.com/v1"
DRY_RUN = False  # Set to False to execute
RATE_LIMIT_DELAY = 0.5

# Team members from the project
TEAM_MEMBERS = [
    14668472,  # Allen Tao - TD
    14631994,  # Chad Paik
    14638981,  # Connor Wilson - TD
    14641060,  # William Wen - TD
    14955890,  # Ai-Ling Ji - MEM
    14668500,  # Amanda Liu - LEAD
    14956954,  # Forest Li - MEM
    14668990,  # Hankun Lin - LEAD
    14641150,  # Jason Park - MEM
]

def assign_resource_to_task(task_id: int, user_id: int, estimated_hours: float) -> bool:
    """Assign a user to a task via API."""
    # Calculate reasonable allocation
    hours_per_day = min(6, estimated_hours / 2)  # Don't exceed 6h/day
    
    payload = {
        "type": "user",
        "type_id": user_id,
        "hours_per_day": round(hours_per_day, 1),
        "total_hours": round(estimated_hours, 1)
    }
    
    cmd = [
        'curl', '-s', '-X', 'POST',
        '-H', f'Authorization: Bearer {API_TOKEN}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload),
        f'{API_BASE}/tasks/{task_id}/resources'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            # Check if successful (has 'data' key or resource info)
            return 'data' in response or 'id' in response
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 80)
    print("Random Resource Assignment for Test Project")
    print("=" * 80)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE EXECUTION'}")
    print(f"Team members available: {len(TEAM_MEMBERS)}")
    print()
    
    # Load tasks
    print("Loading tasks...")
    try:
        with open('/tmp/test_project_tasks.json') as f:
            all_items = json.load(f)
    except FileNotFoundError:
        print("ERROR: Task file not found. Fetching from API...")
        cmd = [
            'curl', '-s',
            '-H', f'Authorization: Bearer {API_TOKEN}',
            f'{API_BASE}/projects/{PROJECT_ID}/children?is_flat_list=true'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        all_items = json.loads(result.stdout)
    
    tasks = [t for t in all_items if t.get('type') in ['task', 'milestone']]
    print(f"Found {len(tasks)} tasks to process")
    print()
    
    # Generate assignments
    assignments = []
    for task in tasks:
        task_id = task['id']
        task_name = task['name']
        estimated_hours = task.get('estimated_hours', 0)
        current_resources = len(task.get('resources', []))
        
        # Skip if already has resources
        if current_resources > 0:
            print(f"⏭️  Skipping {task_name[:40]} (already has {current_resources} resource(s))")
            continue
        
        # Randomly assign 1-3 people
        num_assignees = random.randint(1, 3)
        selected_users = random.sample(TEAM_MEMBERS, num_assignees)
        
        # Split hours among assignees
        hours_per_person = estimated_hours / num_assignees if estimated_hours > 0 else 1.0
        
        for user_id in selected_users:
            assignments.append({
                'task_id': task_id,
                'task_name': task_name,
                'user_id': user_id,
                'hours': hours_per_person,
                'estimated_hours': estimated_hours
            })
    
    # Display preview
    print("=" * 80)
    print("ASSIGNMENT PREVIEW")
    print("=" * 80)
    print(f"\nTotal assignments to create: {len(assignments)}")
    print(f"Tasks to update: {len(set(a['task_id'] for a in assignments))}")
    print()
    
    # Group by task for display
    tasks_summary = {}
    for a in assignments:
        tid = a['task_id']
        if tid not in tasks_summary:
            tasks_summary[tid] = {
                'name': a['task_name'],
                'assignees': [],
                'hours': a['estimated_hours']
            }
        tasks_summary[tid]['assignees'].append(a['user_id'])
    
    print("Sample assignments (first 10 tasks):")
    print(f"{'Task Name':<45} {'Assignees':<15} {'Est.Hrs'}")
    print("-" * 80)
    for i, (tid, info) in enumerate(list(tasks_summary.items())[:10], 1):
        assignee_count = len(info['assignees'])
        print(f"{info['name'][:43]:<45} {assignee_count} people{' '*7} {info['hours']:.1f}h")
    
    if len(tasks_summary) > 10:
        print(f"... and {len(tasks_summary) - 10} more tasks")
    
    print("=" * 80)
    
    if DRY_RUN:
        print("\n✅ DRY RUN COMPLETE - No changes made")
        print("\nTo execute:")
        print("1. Review the preview above")
        print("2. Edit script and set DRY_RUN = False")
        print("3. Run again")
        
        # Save to file
        with open('/tmp/resource_assignments.json', 'w') as f:
            json.dump(assignments, f, indent=2)
        print("\n💾 Assignments saved to: /tmp/resource_assignments.json")
    else:
        print("\n🚀 EXECUTING ASSIGNMENTS...")
        print("=" * 80)
        
        success_count = 0
        fail_count = 0
        
        for i, assignment in enumerate(assignments, 1):
            task_name = assignment['task_name'][:35]
            user_id = assignment['user_id']
            
            print(f"[{i}/{len(assignments)}] Assigning user {user_id} to {task_name}...", end=' ')
            
            if assign_resource_to_task(
                assignment['task_id'],
                assignment['user_id'],
                assignment['hours']
            ):
                print("✅")
                success_count += 1
            else:
                print("❌")
                fail_count += 1
            
            time.sleep(RATE_LIMIT_DELAY)
        
        print("\n" + "=" * 80)
        print("✅ EXECUTION COMPLETE!")
        print(f"\nResults:")
        print(f"  • Successful: {success_count}/{len(assignments)}")
        print(f"  • Failed: {fail_count}/{len(assignments)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
