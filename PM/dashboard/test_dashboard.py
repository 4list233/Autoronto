#!/usr/bin/env python3
"""Test script to diagnose dashboard issues"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("DASHBOARD DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Config loading
print("\n1. Testing config loading...")
try:
    from utils.data_loader import load_config
    config = load_config()
    print(f"   ✓ Config loaded, data_source: {config.get('data_source')}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Data loading
print("\n2. Testing data loading...")
try:
    from utils.data_loader import load_hierarchical_data
    data = load_hierarchical_data()
    print(f"   ✓ Data loaded, {len(data)} root items")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Task extraction
print("\n3. Testing task extraction...")
try:
    from utils.data_loader import get_all_tasks
    tasks = get_all_tasks(data)
    print(f"   ✓ Tasks extracted: {len(tasks)} tasks")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Weekly processor
print("\n4. Testing weekly data processor...")
try:
    from utils.weekly_data_processor import get_available_weeks, get_weekly_member_data
    from datetime import date
    
    weeks = get_available_weeks(tasks, 8, 4)
    print(f"   ✓ Available weeks: {len(weeks)}")
    
    current_week = weeks[8]["start"] if len(weeks) > 8 else date.today()
    member_data = get_weekly_member_data(tasks, current_week, config)
    print(f"   ✓ Weekly member data: {len(member_data)} members")
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Page imports
print("\n5. Testing page imports...")
pages_to_test = [
    ("p1_executive", "pages.p1_executive"),
    ("p10_all_members", "pages.p10_all_members"),
    ("p11_weekly_teams", "pages.p11_weekly_teams"),
]

for page_name, module_name in pages_to_test:
    try:
        __import__(module_name)
        print(f"   ✓ {page_name}")
    except Exception as e:
        print(f"   ✗ {page_name}: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
