#!/usr/bin/env python3
"""
Recalculate task estimates based on duration with realistic assumptions:
- Short tasks (1-7 days): intensive work, ~2-4h per day
- Medium tasks (8-28 days): moderate work, ~1-2h per day
- Long tasks (29-60 days): background work, ~0.5-1h per day
- Very long tasks (60+ days): sporadic work, ~0.3-0.5h per day
"""

import json
import sys
from pathlib import Path

ESTIMATES_FILE = Path(__file__).parent / "task_estimates.json"

def calculate_hours_from_duration(duration_days, task_name, current_hours):
    """
    Calculate realistic hours based on task duration.
    
    Logic:
    - Longer duration doesn't mean proportionally more hours
    - It means work is spread out over time
    - Use different intensity rates based on duration
    """
    
    # Special cases for specific task types
    name_lower = task_name.lower()
    
    # Testing/Validation tasks: typically 1-2 weeks of work regardless of timeline
    if any(keyword in name_lower for keyword in ['testing', 'validation', 'test ']):
        if duration_days <= 7:
            return min(10.0, duration_days * 2)
        elif duration_days <= 21:
            return 15.0
        elif duration_days <= 42:
            return 20.0
        else:
            return 25.0
    
    # Integration tasks: focused work period
    if 'integration' in name_lower or 'integrate' in name_lower:
        if duration_days <= 14:
            return duration_days * 1.5
        elif duration_days <= 35:
            return 25.0
        else:
            return 30.0
    
    # Research tasks: steady but not intensive
    if 'research' in name_lower or 'explore' in name_lower:
        if duration_days <= 30:
            return duration_days * 0.8
        elif duration_days <= 60:
            return 30.0
        else:
            return 35.0
    
    # Training/Tuning ML tasks: compute time, not person time
    if any(keyword in name_lower for keyword in ['train ', 'training', 'fine-tune', 'tune ']):
        if duration_days <= 21:
            return duration_days * 1.0
        elif duration_days <= 42:
            return 25.0
        else:
            return 30.0
    
    # Data collection: mostly automated/waiting
    if 'collect' in name_lower or 'collection' in name_lower:
        if duration_days <= 14:
            return 10.0
        elif duration_days <= 28:
            return 15.0
        else:
            return 20.0
    
    # Presentations/Reports: fixed scope regardless of timeline
    if any(keyword in name_lower for keyword in ['presentation', 'report', 'slides', 'deck']):
        if 'write' in name_lower or 'concept design' in name_lower:
            return 30.0  # Writing takes more time
        return 15.0  # Standard presentation
    
    # Manufacturing/Hardware: hands-on work
    if any(keyword in name_lower for keyword in ['manufacture', 'assembly', 'build', 'fabricate']):
        if duration_days <= 21:
            return duration_days * 1.5
        elif duration_days <= 42:
            return 35.0
        else:
            return 40.0
    
    # CAD/Design work: intensive periods
    if 'cad' in name_lower or 'design' in name_lower:
        if duration_days <= 21:
            return duration_days * 1.5
        elif duration_days <= 42:
            return 30.0
        else:
            return 35.0
    
    # General calculation based on duration tiers
    if duration_days <= 3:
        # Short sprint: intensive 2-3h per day
        return duration_days * 2.5
    elif duration_days <= 7:
        # 1 week: moderate intensity, ~2h per day
        return duration_days * 2.0
    elif duration_days <= 14:
        # 2 weeks: steady work, ~1.5h per day
        return duration_days * 1.5
    elif duration_days <= 28:
        # 1 month: background work, ~1h per day
        return duration_days * 1.0
    elif duration_days <= 42:
        # 6 weeks: periodic work, ~0.7h per day
        return 30.0  # Cap at 30h
    elif duration_days <= 60:
        # 2 months: sporadic work, ~0.5h per day
        return 30.0
    else:
        # Long-running: very sporadic, background task
        return 35.0  # Cap at 35h max

def main():
    print("=" * 100)
    print("Recalculating Task Estimates Based on Duration")
    print("=" * 100)
    
    with open(ESTIMATES_FILE, 'r') as f:
        data = json.load(f)
    
    changes = []
    unchanged = 0
    
    for task_id, task in data['tasks'].items():
        # Skip milestones
        if task['type'] == 'milestone' or task['estimated_hours'] == 0:
            unchanged += 1
            continue
        
        old_hours = task['estimated_hours']
        new_hours = calculate_hours_from_duration(
            task['duration_days'],
            task['name'],
            old_hours
        )
        
        # Round to nearest 0.5
        new_hours = round(new_hours * 2) / 2
        
        # Ensure minimum of 2h for actual tasks
        new_hours = max(2.0, new_hours)
        
        if abs(new_hours - old_hours) > 0.1:
            changes.append({
                'name': task['name'],
                'old': old_hours,
                'new': new_hours,
                'days': task['duration_days'],
                'id': task_id
            })
            
            task['estimated_hours'] = new_hours
            task['source'] = 'duration_based'
            task['confidence'] = 'high'
        else:
            unchanged += 1
    
    # Update total
    total_hours = sum(task['estimated_hours'] for task in data['tasks'].values())
    data['metadata']['total_estimated_hours'] = total_hours
    
    # Save
    with open(ESTIMATES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Recalculated {len(changes)} tasks")
    print(f"✓ {unchanged} tasks unchanged (milestones or manual reviews)")
    print(f"\n{'=' * 100}")
    print(f"SAMPLE CHANGES (showing 30 examples):")
    print(f"{'=' * 100}\n")
    
    # Show sample of changes
    for i, change in enumerate(sorted(changes, key=lambda x: x['old'] - x['new'], reverse=True)[:30], 1):
        diff = change['old'] - change['new']
        print(f"{i}. {change['name']}")
        print(f"   {change['old']}h → {change['new']}h (reduced by {diff}h) | {change['days']} days")
        print(f"   Task ID: {change['id']}")
        print()
    
    if len(changes) > 30:
        print(f"... and {len(changes) - 30} more changes")
    
    print(f"\n{'=' * 100}")
    print(f"SUMMARY:")
    print(f"  - Tasks changed: {len(changes)}")
    print(f"  - Tasks unchanged: {unchanged}")
    print(f"  - New total hours: {total_hours:.1f}h")
    print(f"{'=' * 100}")

if __name__ == "__main__":
    main()
