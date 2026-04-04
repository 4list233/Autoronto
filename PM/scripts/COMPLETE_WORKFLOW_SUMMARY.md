# ✅ Complete Hour Population Workflow - Summary

## 🎯 **Goal:**

Populate realistic actual hours in TeamGantt based on:
- ✅ User roles (Chad/TD/Lead/Member)
- ✅ UofT academic calendar (reading weeks, study weeks, exams)
- ✅ Task complexity (weighted distribution)
- ✅ **NO estimated hours** (only actual time entries)

---

## 📊 **3-Step Process:**

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: ANALYZE TASKS                                          │
│  Script: analyze_tasks.py                                       │
├─────────────────────────────────────────────────────────────────┤
│  Input:  /tmp/test_project_tasks.json (from TeamGantt API)     │
│  Output: task_estimates.json (ACTUAL tasks with estimates)     │
│                                                                 │
│  What it does:                                                  │
│    • Pulls all tasks from project                              │
│    • Analyzes complexity (duration, keywords, type)            │
│    • Estimates hours needed for each task                      │
│    • Saves with task names, IDs, assignments                   │
│                                                                 │
│  Example output:                                                │
│    {                                                            │
│      "12345": {                                                 │
│        "name": "Suspension Design Review",   ← ACTUAL task!    │
│        "estimated_hours": 20.0,              ← Can edit!       │
│        "assigned_to": ["Alice", "Bob"]       ← Real people!    │
│      }                                                          │
│    }                                                            │
└─────────────────────────────────────────────────────────────────┘

                            ↓

┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: REVIEW & ADJUST (OPTIONAL)                             │
│  File: task_estimates.json                                      │
├─────────────────────────────────────────────────────────────────┤
│  Action: Manually review and edit estimates                     │
│                                                                 │
│  Why:                                                           │
│    • Adjust tasks that seem over/under-estimated               │
│    • Prioritize important tasks with more hours                │
│    • Fine-tune based on team knowledge                         │
│                                                                 │
│  How:                                                           │
│    nano task_estimates.json                                    │
│    (Edit estimated_hours for any task)                         │
└─────────────────────────────────────────────────────────────────┘

                            ↓

┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: POPULATE HOURS                                         │
│  Script: populate_actual_hours.py                               │
├─────────────────────────────────────────────────────────────────┤
│  Input:  task_estimates.json + user_roles.json                 │
│  Output: Time entries in TeamGantt                             │
│                                                                 │
│  What it does:                                                  │
│    FOR EACH user:                                               │
│      FOR EACH week:                                             │
│        1. Sample weekly hours (role-based)                     │
│        2. Apply calendar modifier (reading/exam weeks)         │
│        3. Get user's tasks for this week                       │
│        4. Weight tasks by estimates from file                  │
│        5. Distribute hours proportionally                      │
│        6. Create time blocks (Mon-Fri)                         │
│                                                                 │
│  Example:                                                       │
│    Alice (Member): 10h this week                               │
│    Tasks from task_estimates.json:                             │
│      • Task 12345 (20h) → 44% → 4.4h                          │
│      • Task 12346 (15h) → 33% → 3.3h                          │
│      • Task 12347 (10h) → 22% → 2.2h                          │
│    Total: 10h ✅                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 **Quick Commands:**

### **Full Workflow:**
```bash
cd scripts

# Step 1: Analyze
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
python3 analyze_tasks.py

# Step 2: Review (optional)
nano task_estimates.json

# Step 3: Populate
nano user_roles.json
python3 populate_actual_hours.py  # Dry run
# (Edit: DRY_RUN = False)
python3 populate_actual_hours.py  # Execute
```

---

## 📂 **Files Explained:**

### **Configuration Files (You Edit):**

| File | Purpose | When to Edit |
|------|---------|--------------|
| **`.env`** | API credentials | Once (setup) |
| **`user_roles.json`** | User → role mapping | When team changes |
| **`academic_calendar.json`** | UofT calendar dates | Once (setup) |
| **`task_estimates.json`** | Task → hours estimates | After analyzing, optional |

### **Generated Files (Scripts Create):**

| File | Created By | Contains |
|------|------------|----------|
| **`data/children_flat_*.json`** | `fetch_teamgantt_data.sh` | Raw tasks from API |
| **`/tmp/test_project_tasks.json`** | You (copy) | Tasks ready for analysis |
| **`task_estimates.json`** | `analyze_tasks.py` | Analyzed task estimates |
| **`/tmp/actual_hours_population_plan.json`** | `populate_actual_hours.py` | Dry run preview |

---

## 🎓 **Role Configurations:**

| Role | Hours/Week | Range | Calendar | Overhead |
|------|------------|-------|----------|----------|
| **Chad (PhD)** | 12h | 9-15h | PhD (year-round) | No |
| **TD** | 12h | 9-15h | Undergrad | Yes (37.5%) |
| **Lead** | 10.5h | 8-13h | Undergrad | No |
| **Member** | 8.5h | 7-10h | Undergrad | No |
| **Inactive** | 3h | 0-6h | Undergrad | No |

---

## 📅 **Calendar Modifiers:**

| Period | Multiplier | Applies To |
|--------|------------|------------|
| **Reading Week** | 1.5× | Undergrads only |
| **Study Week** | 0.5× | Undergrads only |
| **Exam Week** | 0.3× | Undergrads only |
| **Summer** | 1.3× | Undergrads only |
| **Summer (PhD)** | 1.2× | PhD students only |
| **Normal** | 1.0× | Everyone |

---

## 🔍 **Task Estimate Sources:**

### **Priority 1: TeamGantt (High Confidence)**
```
Task has estimated_hours field set
→ Use that value directly
```

### **Priority 2: Calculated (Medium Confidence)**
```
Task has dates but no estimated_hours
→ Calculate: duration_days × 2h/day
→ Adjust with keyword multipliers:
   - "design/implementation" → 1.5×
   - "report/proposal" → 2.0×
   - "meeting/review" → 0.5×
```

### **Priority 3: Default (Low Confidence)**
```
Task has no dates or estimate
→ Use 5h default
```

---

## 📊 **Example Outputs:**

### **Step 1: analyze_tasks.py**
```
ANALYSIS SUMMARY
═══════════════════════════════════════════════════════════════

Total tasks analyzed: 147
Estimates from TeamGantt: 23
Estimates calculated: 124
Total project hours: 1,847.5h

Sample task estimates:
Task Name                                     Type       Est.     Source
─────────────────────────────────────────────────────────────────────────
Suspension Design Review                      task       20.0h    calculated
Brake System Integration                      task       15.5h    teamgantt
Vehicle Testing Preparation                   task       12.0h    calculated
Weekly Team Meeting                           task        2.0h    calculated
Final Report Writing                          task       35.0h    calculated

✅ Task estimates saved to: scripts/task_estimates.json
```

### **Step 3: populate_actual_hours.py (Dry Run)**
```
Loading task estimates...
  ✓ Loaded estimates for 147 tasks

User: Alice Brown (Role: member)
  ✓ 24 weeks active, 195.0h total

User: Bob Wilson (Role: td)
  ✓ 24 weeks active, 276.0h total
    ├─ Overhead: 103.5h (37.5%)
    └─ Tasks: 172.5h

SUMMARY
User                      Role         Total Hours  Weeks   Avg/Week
─────────────────────────────────────────────────────────────────────
Chad                      chad_phd          288.0h     24      12.0h
Bob Wilson                td                276.0h     24      11.5h
Jane Smith                lead              246.0h     24      10.3h
Alice Brown               member            204.0h     24       8.5h

TASK WEIGHTING EXAMPLE
═══════════════════════════════════════════════════════════════

Example:
  User has 10h this week, 3 tasks assigned:
    • Suspension Design (20h est) → 44% → 4.4h this week
    • Testing Prep (15h est) → 33% → 3.3h this week
    • Documentation (10h est) → 22% → 2.2h this week
  Total: 10h (matches user's weekly allocation)

✅ DRY RUN COMPLETE - No changes were made
```

---

## ✅ **Key Benefits:**

1. **Actual Task Data**: `task_estimates.json` has real task names, not placeholders
2. **Reviewable**: You can review and adjust estimates before populating
3. **Source of Truth**: Estimates persist in a file you can reference
4. **Weighted Distribution**: Hours distributed by task complexity
5. **No Estimated Hours**: Script only creates actual time entries

---

**See `WORKFLOW_GUIDE.md` for complete step-by-step instructions!** 🚀
