#!/usr/bin/env python3
"""
TeamGantt Data Analyzer
Analyzes exported TeamGantt data and identifies issues:
- Missing task titles
- Tasks without hour estimates
- Poor WBS structure
- Missing dependencies
"""

import json
import csv
import pandas as pd
from collections import defaultdict
from pathlib import Path

def load_data():
    """Load CSV and JSON data"""
    csv_file = Path("teamgantt_export_4336931.csv")
    json_file = Path("children_flat_4336931.json")
    
    # Load CSV
    df = pd.read_csv(csv_file)
    
    # Load JSON
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    return df, json_data

def analyze_structure(df):
    """Analyze WBS structure and identify issues"""
    print("\n" + "="*80)
    print("📊 PROJECT STRUCTURE ANALYSIS")
    print("="*80)
    
    # Count by type
    type_counts = df['Type'].value_counts()
    print(f"\n📦 Item Counts:")
    for item_type, count in type_counts.items():
        print(f"  • {item_type:12s}: {count:3d}")
    
    # Groups analysis
    groups = df[df['Type'] == 'group']
    print(f"\n📁 Groups ({len(groups)}):")
    for _, row in groups.iterrows():
        wbs = row['WBS #']
        name = row['Name / Title']
        est_hours = row['Estimated Hours']
        actual_hours = row['Actual Hours']
        progress = row['Progress (%)']
        print(f"  {wbs:8s} {name:30s} | Est: {est_hours:5.1f}h | Act: {actual_hours:5.1f}h | {progress:5.1f}%")

def analyze_missing_titles(df):
    """Find tasks with missing or poor titles"""
    print("\n" + "="*80)
    print("⚠️  MISSING OR POOR TITLES")
    print("="*80)
    
    issues = []
    
    for idx, row in df.iterrows():
        wbs = row['WBS #']
        title = str(row['Name / Title']).strip()
        item_type = row['Type']
        
        # Skip project and group names (they're usually OK)
        if item_type in ['project', 'group', 'subgroup']:
            continue
            
        # Check for missing/empty titles
        if not title or title == 'nan' or len(title) < 3:
            issues.append({
                'wbs': wbs,
                'type': item_type,
                'title': title,
                'issue': 'Missing or too short'
            })
        # Check for generic/placeholder titles
        elif any(x in title.lower() for x in ['unnamed', 'task', 'todo', 'untitled', 'new ']):
            issues.append({
                'wbs': wbs,
                'type': item_type,
                'title': title,
                'issue': 'Generic placeholder'
            })
    
    if issues:
        print(f"\n❌ Found {len(issues)} title issues:")
        for issue in issues[:20]:  # Show first 20
            print(f"  {issue['wbs']:8s} [{issue['type']:8s}] {issue['title']:40s} → {issue['issue']}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("\n✅ No major title issues found!")
    
    return issues

def analyze_hours(df):
    """Analyze hour estimates and identify gaps"""
    print("\n" + "="*80)
    print("⏱️  HOUR ESTIMATION ANALYSIS")
    print("="*80)
    
    # Filter to tasks only (not groups/milestones)
    tasks = df[df['Type'] == 'task'].copy()
    
    # Missing estimates
    no_estimate = tasks[tasks['Estimated Hours'] == 0]
    has_estimate = tasks[tasks['Estimated Hours'] > 0]
    
    print(f"\n📈 Overall Stats:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  With estimates: {len(has_estimate)} ({len(has_estimate)/len(tasks)*100:.1f}%)")
    print(f"  Missing estimates: {len(no_estimate)} ({len(no_estimate)/len(tasks)*100:.1f}%)")
    
    if len(has_estimate) > 0:
        print(f"\n  Total estimated hours: {has_estimate['Estimated Hours'].sum():.1f}h")
        print(f"  Total actual hours: {tasks['Actual Hours'].sum():.1f}h")
        print(f"  Average estimate per task: {has_estimate['Estimated Hours'].mean():.1f}h")
    
    # Tasks missing estimates
    if len(no_estimate) > 0:
        print(f"\n❌ Tasks missing hour estimates ({len(no_estimate)}):")
        for idx, row in no_estimate.head(15).iterrows():
            wbs = row['WBS #']
            title = row['Name / Title']
            actual = row['Actual Hours']
            progress = row['Progress (%)']
            print(f"  {wbs:8s} {title:50s} | Act: {actual:5.1f}h | {progress:5.1f}%")
        if len(no_estimate) > 15:
            print(f"  ... and {len(no_estimate) - 15} more")
    
    return no_estimate

def analyze_dependencies(df):
    """Analyze task dependencies"""
    print("\n" + "="*80)
    print("🔗 DEPENDENCY ANALYSIS")
    print("="*80)
    
    tasks = df[df['Type'] == 'task']
    with_deps = tasks[tasks['Predecessors'].notna() & (tasks['Predecessors'] != '')]
    without_deps = tasks[tasks['Predecessors'].isna() | (tasks['Predecessors'] == '')]
    
    print(f"\n  Tasks with dependencies: {len(with_deps)} ({len(with_deps)/len(tasks)*100:.1f}%)")
    print(f"  Tasks without dependencies: {len(without_deps)} ({len(without_deps)/len(tasks)*100:.1f}%)")
    
    if len(with_deps) > 0:
        print(f"\n✅ Sample tasks with dependencies:")
        for idx, row in with_deps.head(5).iterrows():
            wbs = row['WBS #']
            title = row['Name / Title']
            deps = row['Predecessors']
            print(f"  {wbs:8s} {title:40s} → depends on: {deps}")

def analyze_progress(df):
    """Analyze overall project progress"""
    print("\n" + "="*80)
    print("📊 PROGRESS SUMMARY")
    print("="*80)
    
    tasks = df[df['Type'] == 'task']
    
    # Progress categories
    not_started = tasks[tasks['Progress (%)'] == 0]
    in_progress = tasks[(tasks['Progress (%)'] > 0) & (tasks['Progress (%)'] < 100)]
    completed = tasks[tasks['Progress (%)'] == 100]
    
    print(f"\n  Not Started: {len(not_started):3d} ({len(not_started)/len(tasks)*100:5.1f}%)")
    print(f"  In Progress: {len(in_progress):3d} ({len(in_progress)/len(tasks)*100:5.1f}%)")
    print(f"  Completed:   {len(completed):3d} ({len(completed)/len(tasks)*100:5.1f}%)")
    print(f"\n  Overall completion: {tasks['Progress (%)'].mean():.1f}%")
    
    # Group breakdown
    print(f"\n📁 Progress by Group:")
    for _, group in df[df['Type'] == 'group'].iterrows():
        wbs = group['WBS #']
        name = group['Name / Title']
        progress = group['Progress (%)']
        # Count tasks in this group
        group_tasks = tasks[tasks['WBS #'].str.startswith(wbs + '.')]
        print(f"  {name:25s} {progress:5.1f}% ({len(group_tasks)} tasks)")

def generate_recommendations(df, no_estimate_tasks):
    """Generate actionable recommendations"""
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    print("""
1. 🔧 FIX MISSING HOUR ESTIMATES
   - Add estimates to {count} tasks without hours
   - Use rule: leads get +30% hours, members use base estimate
   
2. 📝 CLEAN UP STRUCTURE
   - Review WBS hierarchy for logical grouping
   - Ensure consistent naming conventions
   
3. 🔗 ADD DEPENDENCIES
   - Only {dep_pct:.1f}% of tasks have dependencies
   - Add FS (Finish-to-Start) relationships for sequential work
   
4. ✅ NEXT STEPS
   - I can generate bulk API payloads to update all tasks
   - Or create a clean CSV for re-import
   - Specify your hour estimation rules (e.g., "Design tasks = 10h, Implementation = 30h")
""".format(
        count=len(no_estimate_tasks),
        dep_pct=(df[df['Type'] == 'task']['Predecessors'].notna().sum() / len(df[df['Type'] == 'task']) * 100)
    ))

def main():
    """Main analysis workflow"""
    print("\n🚀 TeamGantt Project Analysis")
    print("="*80)
    
    # Load data
    df, json_data = load_data()
    
    print(f"\n✅ Loaded:")
    print(f"   • CSV: {len(df)} rows")
    print(f"   • JSON: {len(json_data)} items")
    
    # Run analyses
    analyze_structure(df)
    title_issues = analyze_missing_titles(df)
    no_estimate = analyze_hours(df)
    analyze_dependencies(df)
    analyze_progress(df)
    generate_recommendations(df, no_estimate)
    
    print("\n" + "="*80)
    print("✨ Analysis complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
