#!/usr/bin/env python3
"""
Review and update task estimates:
1. Set all milestones to 0 hours (they're just check-ins)
2. Identify ambiguous estimates for manual review
"""

import json
import sys
from pathlib import Path

# Load task estimates
ESTIMATES_FILE = Path(__file__).parent / "task_estimates.json"

def load_estimates():
    with open(ESTIMATES_FILE, 'r') as f:
        return json.load(f)

def save_estimates(data):
    with open(ESTIMATES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def identify_ambiguous_tasks(data):
    """Identify tasks that might need manual review"""
    ambiguous = []
    
    for task_id, task in data['tasks'].items():
        reasons = []
        
        # Skip milestones (we're setting those to 0)
        if task['type'] == 'milestone':
            continue
            
        # Very short tasks (< 2 hours) might be underestimated
        if task['estimated_hours'] < 2 and task['duration_days'] > 1:
            reasons.append(f"Low estimate ({task['estimated_hours']}h) for {task['duration_days']} days")
        
        # Very long tasks (> 50 hours) might need breakdown
        if task['estimated_hours'] > 50:
            reasons.append(f"High estimate ({task['estimated_hours']}h) - might need breakdown")
        
        # Tasks with vague names
        vague_keywords = ['misc', 'other', 'tbd', 'todo', 'temp', 'test', 'placeholder']
        if any(keyword in task['name'].lower() for keyword in vague_keywords):
            reasons.append("Vague task name")
        
        # Tasks with 1-day duration but > 10 hours (might be placeholders)
        if task['duration_days'] == 1 and task['estimated_hours'] > 10:
            reasons.append(f"1 day duration but {task['estimated_hours']}h estimate")
        
        # Tasks with medium/low confidence and high hours
        if task['confidence'] == 'medium' and task['estimated_hours'] > 30:
            reasons.append(f"Medium confidence with {task['estimated_hours']}h")
        
        if reasons:
            ambiguous.append({
                'id': task_id,
                'name': task['name'],
                'estimated_hours': task['estimated_hours'],
                'duration_days': task['duration_days'],
                'confidence': task['confidence'],
                'source': task['source'],
                'reasons': reasons
            })
    
    return ambiguous

def main():
    print("=" * 80)
    print("Task Estimates Review")
    print("=" * 80)
    
    # Load data
    data = load_estimates()
    
    # Find all milestones
    milestones = []
    milestone_count = 0
    for task_id, task in data['tasks'].items():
        if task['type'] == 'milestone' or 'milestone' in task['name'].lower():
            if task['estimated_hours'] != 0:
                milestones.append(f"  - {task['name']}: {task['estimated_hours']}h → 0h")
                task['estimated_hours'] = 0
                milestone_count += 1
    
    print(f"\n✓ Found {milestone_count} milestones to set to 0 hours:")
    for m in milestones[:10]:  # Show first 10
        print(m)
    if len(milestones) > 10:
        print(f"  ... and {len(milestones) - 10} more")
    
    # Update metadata
    total_hours = sum(task['estimated_hours'] for task in data['tasks'].values())
    data['metadata']['total_estimated_hours'] = total_hours
    
    # Save updated estimates
    save_estimates(data)
    print(f"\n✓ Updated task_estimates.json (new total: {total_hours}h)")
    
    # Identify ambiguous tasks
    print("\n" + "=" * 80)
    print("AMBIGUOUS TASKS FOR MANUAL REVIEW")
    print("=" * 80)
    
    ambiguous = identify_ambiguous_tasks(data)
    
    if not ambiguous:
        print("\n✓ No ambiguous tasks found! All estimates look reasonable.")
    else:
        print(f"\nFound {len(ambiguous)} tasks that might need review:\n")
        
        for i, task in enumerate(ambiguous, 1):
            print(f"{i}. {task['name']}")
            print(f"   Estimate: {task['estimated_hours']}h over {task['duration_days']} days")
            print(f"   Confidence: {task['confidence']} | Source: {task['source']}")
            print(f"   Reasons: {', '.join(task['reasons'])}")
            print(f"   Task ID: {task['id']}")
            print()
    
    print("=" * 80)
    print(f"Summary:")
    print(f"  - {milestone_count} milestones set to 0h")
    print(f"  - {len(ambiguous)} tasks flagged for review")
    print(f"  - Total project hours: {total_hours}h")
    print("=" * 80)

if __name__ == "__main__":
    main()
