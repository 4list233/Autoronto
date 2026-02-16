#!/usr/bin/env python3
"""
Analyze TeamGantt tasks and create estimates for hour weighting.

This script:
1. Pulls tasks from TeamGantt API
2. Analyzes each task (duration, complexity, existing estimates)
3. Calculates estimated hours needed to complete
4. Saves to task_estimates.json for use by populate_actual_hours.py

Run this BEFORE populate_actual_hours.py to create the weighting baseline.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

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

# Configuration
API_TOKEN = os.getenv('TEAMGANTT_API_KEY', '')
PROJECT_ID = int(os.getenv('TEAMGANTT_PROJECT_ID', '0'))

if not API_TOKEN or not PROJECT_ID:
    print("❌ ERROR: Missing API credentials in .env file")
    sys.exit(1)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_duration_days(task):
    """Calculate task duration in days."""
    try:
        start = datetime.fromisoformat(task.get('start_date', '').replace('Z', '+00:00'))
        end = datetime.fromisoformat(task.get('end_date', '').replace('Z', '+00:00'))
        duration = max(1, (end - start).days + 1)  # +1 to include both start and end days
        return duration
    except:
        return 5  # Default

def analyze_task_complexity(task):
    """
    Analyze task and estimate hours needed to complete.
    
    Returns:
        dict: {
            'estimated_hours': float,
            'source': str ('teamgantt' or 'calculated'),
            'confidence': str ('high', 'medium', 'low')
        }
    """
    task_name = task.get('name', '').lower()
    
    # Priority 1: Use TeamGantt's estimated_hours if available
    estimated_hours = task.get('estimated_hours', 0)
    if estimated_hours and estimated_hours > 0:
        return {
            'estimated_hours': estimated_hours,
            'source': 'teamgantt',
            'confidence': 'high'
        }
    
    # Priority 2: Calculate from duration
    duration_days = calculate_duration_days(task)
    
    # Baseline: 2 hours per day
    base_estimate = duration_days * 2.0
    
    # Adjust based on task type keywords
    multiplier = 1.0
    confidence = 'medium'
    
    # High complexity keywords (more hours per day)
    if any(kw in task_name for kw in ['design', 'implementation', 'development', 'research', 'analysis']):
        multiplier = 1.5
        confidence = 'medium'
    
    # Major deliverables (much more hours)
    elif any(kw in task_name for kw in ['report', 'presentation', 'proposal', 'documentation']):
        multiplier = 2.0
        confidence = 'medium'
    
    # Low complexity keywords (fewer hours per day)
    elif any(kw in task_name for kw in ['meeting', 'review', 'update', 'admin']):
        multiplier = 0.5
        confidence = 'medium'
    
    # Milestones (very low hours)
    elif task.get('type') == 'milestone':
        multiplier = 0.2
        confidence = 'high'
    
    estimated_hours = base_estimate * multiplier
    
    # Clamp to reasonable range (0.5h - 50h)
    estimated_hours = max(0.5, min(50.0, estimated_hours))
    
    return {
        'estimated_hours': round(estimated_hours, 1),
        'source': 'calculated',
        'confidence': confidence
    }

# ============================================================================
# MAIN LOGIC
# ============================================================================

def main():
    print("=" * 80)
    print("TeamGantt Task Analysis - Create Weighting Baseline")
    print("=" * 80)
    print(f"Project ID: {PROJECT_ID}")
    print()
    
    # Load tasks
    print("Loading tasks from /tmp/test_project_tasks.json...")
    try:
        with open('/tmp/test_project_tasks.json') as f:
            all_items = json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: Task file not found")
        print("Run: ./fetch_teamgantt_data.sh first")
        print("Then: cp ../data/children_flat_<PROJECT_ID>.json /tmp/test_project_tasks.json")
        return 1
    
    # Filter to only tasks and milestones
    all_tasks = [t for t in all_items if t.get('type') in ['task', 'milestone']]
    print(f"  ✓ Found {len(all_tasks)} tasks/milestones to analyze")
    print()
    
    # Analyze each task
    print("Analyzing tasks...")
    task_estimates = {}
    
    stats = {
        'from_teamgantt': 0,
        'calculated': 0,
        'total_hours': 0
    }
    
    for task in all_tasks:
        task_id = str(task['id'])
        task_name = task.get('name', 'Unknown')
        task_type = task.get('type', 'task')
        
        # Analyze complexity
        analysis = analyze_task_complexity(task)
        
        # Get additional metadata
        duration_days = calculate_duration_days(task)
        start_date = task.get('start_date', '')
        end_date = task.get('end_date', '')
        resources = task.get('resources', [])
        
        # Store estimate
        task_estimates[task_id] = {
            'name': task_name,
            'type': task_type,
            'estimated_hours': analysis['estimated_hours'],
            'source': analysis['source'],
            'confidence': analysis['confidence'],
            'duration_days': duration_days,
            'start_date': start_date[:10] if start_date else '',
            'end_date': end_date[:10] if end_date else '',
            'assigned_to': [r.get('name', '') for r in resources]
        }
        
        # Update stats
        if analysis['source'] == 'teamgantt':
            stats['from_teamgantt'] += 1
        else:
            stats['calculated'] += 1
        stats['total_hours'] += analysis['estimated_hours']
    
    print(f"  ✓ Analyzed {len(task_estimates)} tasks")
    print()
    
    # Display summary
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    print(f"Total tasks analyzed: {len(task_estimates)}")
    print(f"Estimates from TeamGantt: {stats['from_teamgantt']}")
    print(f"Estimates calculated: {stats['calculated']}")
    print(f"Total project hours: {stats['total_hours']:.1f}h")
    print()
    
    # Show sample estimates
    print("Sample task estimates (first 15):")
    print(f"{'Task Name':<45} {'Type':<10} {'Est.':<8} {'Source':<12} {'Duration':<8}")
    print("-" * 90)
    
    for i, (task_id, estimate) in enumerate(list(task_estimates.items())[:15]):
        print(f"{estimate['name'][:43]:<45} {estimate['type']:<10} "
              f"{estimate['estimated_hours']:>6.1f}h {estimate['source']:<12} "
              f"{estimate['duration_days']:>6}d")
    
    if len(task_estimates) > 15:
        print(f"... and {len(task_estimates) - 15} more tasks")
    
    print()
    
    # Show confidence breakdown
    confidence_counts = {}
    for est in task_estimates.values():
        conf = est['confidence']
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
    
    print("Confidence levels:")
    for conf, count in sorted(confidence_counts.items()):
        pct = (count / len(task_estimates)) * 100
        print(f"  {conf.capitalize()}: {count} tasks ({pct:.1f}%)")
    
    print()
    print("=" * 80)
    
    # Save to file
    output_file = Path(__file__).parent / 'task_estimates.json'
    
    output_data = {
        'metadata': {
            'project_id': PROJECT_ID,
            'generated_at': datetime.now().isoformat(),
            'total_tasks': len(task_estimates),
            'total_estimated_hours': stats['total_hours'],
            'from_teamgantt': stats['from_teamgantt'],
            'calculated': stats['calculated']
        },
        'tasks': task_estimates
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print()
    print(f"✅ Task estimates saved to: {output_file}")
    print()
    print("Next steps:")
    print("  1. Review task_estimates.json and manually adjust any estimates if needed")
    print("  2. Run populate_actual_hours.py to use these estimates for hour distribution")
    print()
    print("To manually edit estimates:")
    print(f"  nano {output_file}")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
