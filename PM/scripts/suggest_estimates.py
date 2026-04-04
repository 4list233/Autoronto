#!/usr/bin/env python3
"""
Hour Estimation Strategy Generator
Analyzes actual hours logged and suggests estimation approaches
"""

import json
import csv
import pandas as pd
from collections import defaultdict
from pathlib import Path

def load_data():
    """Load CSV data"""
    csv_file = Path("data/teamgantt_export_4336931.csv")
    df = pd.read_csv(csv_file)
    return df

def analyze_completed_tasks(df):
    """Analyze completed tasks to find patterns"""
    print("\n" + "="*80)
    print("📊 ANALYZING COMPLETED TASKS (100% Progress)")
    print("="*80)
    
    completed = df[(df['Type'] == 'task') & (df['Progress (%)'] == 100)].copy()
    
    print(f"\n✅ Found {len(completed)} completed tasks with actual hours logged\n")
    
    # Group by WBS prefix (team)
    completed['Team'] = completed['WBS #'].str.extract(r'^(\d+\.\d+)')[0]
    
    # Stats by team
    team_stats = completed.groupby('Team').agg({
        'Actual Hours': ['count', 'sum', 'mean', 'median', 'min', 'max']
    }).round(1)
    
    print("Hours breakdown by team (completed tasks only):")
    print(team_stats.to_string())
    
    # Overall stats
    print(f"\n📈 Overall Statistics:")
    print(f"  Mean hours per completed task: {completed['Actual Hours'].mean():.1f}h")
    print(f"  Median hours per completed task: {completed['Actual Hours'].median():.1f}h")
    print(f"  Total hours in completed tasks: {completed['Actual Hours'].sum():.1f}h")
    
    return completed

def analyze_in_progress_tasks(df):
    """Analyze in-progress tasks to calculate projected totals"""
    print("\n" + "="*80)
    print("🔄 ANALYZING IN-PROGRESS TASKS")
    print("="*80)
    
    in_progress = df[(df['Type'] == 'task') & 
                     (df['Progress (%)'] > 0) & 
                     (df['Progress (%)'] < 100)].copy()
    
    print(f"\n🟡 Found {len(in_progress)} in-progress tasks\n")
    
    # Calculate projected hours based on progress
    in_progress['Projected Hours'] = (in_progress['Actual Hours'] / 
                                       (in_progress['Progress (%)'] / 100)).round(1)
    
    for idx, row in in_progress.head(15).iterrows():
        wbs = row['WBS #']
        title = row['Name / Title'][:40]
        actual = row['Actual Hours']
        progress = row['Progress (%)']
        projected = row['Projected Hours']
        
        print(f"  {wbs:8s} {title:40s} | {actual:5.1f}h @ {progress:5.1f}% → est {projected:5.1f}h")
    
    if len(in_progress) > 15:
        print(f"  ... and {len(in_progress) - 15} more")
    
    return in_progress

def suggest_estimation_strategies(df, completed, in_progress):
    """Suggest different estimation approaches"""
    print("\n" + "="*80)
    print("💡 ESTIMATION STRATEGY SUGGESTIONS")
    print("="*80)
    
    tasks = df[df['Type'] == 'task'].copy()
    not_started = tasks[tasks['Progress (%)'] == 0]
    
    print(f"""
We have:
  ✅ {len(completed)} completed tasks (with actual hours)
  🟡 {len(in_progress)} in-progress tasks (partial hours)
  ❌ {len(not_started)} not-started tasks (no hours yet)

Here are 5 estimation strategies to consider:
""")
    
    # Strategy 1: Use actual hours directly
    print("\n" + "-"*80)
    print("STRATEGY 1: Mirror Actual Hours (Conservative)")
    print("-"*80)
    print("""
For completed tasks: estimate = actual hours
For in-progress: estimate = actual / (progress%)
For not-started: use team average from completed tasks

✅ Pros: Based on real data, defensible
❌ Cons: May underestimate future complexity
    
Estimate totals:
""")
    
    completed_est = completed['Actual Hours'].sum()
    in_progress_est = (in_progress['Actual Hours'] / (in_progress['Progress (%)'] / 100)).sum()
    
    # Team averages for not started
    completed['Team'] = completed['WBS #'].str.extract(r'^(\d+\.\d+)')[0]
    team_avg = completed.groupby('Team')['Actual Hours'].mean().to_dict()
    
    not_started_est = 0
    for idx, row in not_started.iterrows():
        team = row['WBS #'].split('.')[0] + '.' + row['WBS #'].split('.')[1]
        avg = team_avg.get(team, completed['Actual Hours'].mean())
        not_started_est += avg
    
    total_s1 = completed_est + in_progress_est + not_started_est
    print(f"  Completed tasks: {completed_est:.0f}h")
    print(f"  In-progress tasks: {in_progress_est:.0f}h")
    print(f"  Not-started tasks: {not_started_est:.0f}h")
    print(f"  TOTAL ESTIMATE: {total_s1:.0f}h")
    
    # Strategy 2: Add buffer
    print("\n" + "-"*80)
    print("STRATEGY 2: Actual Hours + 20% Buffer (Realistic)")
    print("-"*80)
    print("""
Same as Strategy 1, but add 20% buffer for:
- Unexpected issues
- Integration time
- Testing overhead

✅ Pros: Accounts for unknowns
❌ Cons: May seem padded to stakeholders
    
Estimate totals:
""")
    total_s2 = total_s1 * 1.2
    print(f"  Base estimate: {total_s1:.0f}h")
    print(f"  With 20% buffer: {total_s2:.0f}h")
    
    # Strategy 3: Role-based
    print("\n" + "-"*80)
    print("STRATEGY 3: Role-Based (LEAD vs MEMBER)")
    print("-"*80)
    print("""
Analyze who's assigned and apply multipliers:
- Tasks with LEAD in assignment: +30% hours
- Tasks with only MEMs: use base hours
- Mixed assignments: use weighted average

✅ Pros: Recognizes leadership overhead
❌ Cons: Requires parsing all assignments
    
Sample calculation:
""")
    
    # Count lead vs member tasks
    lead_tasks = 0
    member_tasks = 0
    for idx, row in completed.iterrows():
        assigned = str(row['Assigned']).upper()
        if 'LEAD' in assigned:
            lead_tasks += 1
        else:
            member_tasks += 1
    
    if lead_tasks > 0:
        lead_avg = completed[completed['Assigned'].str.contains('LEAD', case=False, na=False)]['Actual Hours'].mean()
        member_avg = completed[~completed['Assigned'].str.contains('LEAD', case=False, na=False)]['Actual Hours'].mean()
        print(f"  Average for LEAD tasks: {lead_avg:.1f}h")
        print(f"  Average for MEMBER tasks: {member_avg:.1f}h")
        print(f"  Lead multiplier: {lead_avg/member_avg:.2f}x")
    
    # Strategy 4: Task category
    print("\n" + "-"*80)
    print("STRATEGY 4: Task Category Heuristics")
    print("-"*80)
    print("""
Categorize tasks by keywords and apply standard estimates:

- "Setup", "Environment", "Onboarding": 10-15h
- "Integration", "C++", "Implementation": 30-50h
- "Testing", "Debug", "Validation": 20-30h
- "Documentation", "Review": 5-10h
- "Research", "Analysis": 15-25h

✅ Pros: Industry-standard estimates
❌ Cons: May not match your team's velocity
""")
    
    # Strategy 5: Fibonacci
    print("\n" + "-"*80)
    print("STRATEGY 5: T-Shirt Sizing → Fibonacci Hours")
    print("-"*80)
    print("""
Bucket tasks into sizes, then assign Fibonacci hours:

- XS (Simple): 2h
- S (Small): 5h
- M (Medium): 13h
- L (Large): 21h
- XL (Complex): 34h

Based on current data distribution:
""")
    
    percentiles = completed['Actual Hours'].quantile([0.2, 0.4, 0.6, 0.8])
    print(f"  XS (0-20%): 0-{percentiles[0.2]:.0f}h → assign 2h")
    print(f"  S (20-40%): {percentiles[0.2]:.0f}-{percentiles[0.4]:.0f}h → assign 5h")
    print(f"  M (40-60%): {percentiles[0.4]:.0f}-{percentiles[0.6]:.0f}h → assign 13h")
    print(f"  L (60-80%): {percentiles[0.6]:.0f}-{percentiles[0.8]:.0f}h → assign 21h")
    print(f"  XL (80-100%): {percentiles[0.8]:.0f}h+ → assign 34h")
    
    print("\n✅ Pros: Simple, prevents over-precision")
    print("❌ Cons: Less granular")

def generate_team_benchmarks(df, completed):
    """Generate benchmarks by team"""
    print("\n" + "="*80)
    print("📊 TEAM-SPECIFIC BENCHMARKS")
    print("="*80)
    
    completed['Team'] = completed['WBS #'].str.extract(r'^(\d+\.\d+)')[0]
    
    # Map team codes to names
    team_names = {
        '1.1': 'Recruitment',
        '1.2': '2DOD',
        '1.3': '3DOD',
        '1.6': 'Localization',
        '1.7': 'Planning',
        '1.8': 'Mapping',
        '1.9': 'Simulation',
        '1.10': 'Electrical',
        '1.11': 'Mechanical',
        '1.13': 'Systems Software',
        '1.14': 'GUI',
        '1.16': 'Mob. Innovation'
    }
    
    print("\nAverage hours per completed task by team:")
    print("-" * 60)
    
    benchmarks = {}
    for team_code, team_name in team_names.items():
        team_tasks = completed[completed['Team'] == team_code]
        if len(team_tasks) > 0:
            avg = team_tasks['Actual Hours'].mean()
            median = team_tasks['Actual Hours'].median()
            count = len(team_tasks)
            benchmarks[team_name] = {'avg': avg, 'median': median, 'count': count}
            print(f"  {team_name:25s} | {count:2d} tasks | Avg: {avg:5.1f}h | Median: {median:5.1f}h")
    
    return benchmarks

def main():
    """Main analysis workflow"""
    print("\n🎯 Hour Estimation Strategy Analysis")
    print("="*80)
    
    df = load_data()
    
    completed = analyze_completed_tasks(df)
    in_progress = analyze_in_progress_tasks(df)
    suggest_estimation_strategies(df, completed, in_progress)
    benchmarks = generate_team_benchmarks(df, completed)
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("="*80)
    print("""
1. Choose your preferred estimation strategy (1-5)
2. I'll generate a CSV with proposed estimates
3. Review and adjust estimates manually
4. Once approved, I'll create API payloads to bulk-update TeamGantt

Which strategy appeals to you most? Or mix multiple approaches?
""")

if __name__ == "__main__":
    main()
