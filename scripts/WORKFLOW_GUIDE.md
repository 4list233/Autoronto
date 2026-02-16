# 🔄 Complete Workflow - Role-Based Hour Population

## 📋 **Overview:**

This is a **3-step process**:

1. **Analyze Tasks** → Pull from API, estimate hours, save locally
2. **Review & Edit** → Manually adjust estimates if needed
3. **Populate Hours** → Use estimates to distribute hours across users

---

## 🚀 **Complete Workflow:**

### **Step 1: Analyze Tasks (One-Time Setup)**

Pull tasks from TeamGantt and create weighting baseline:

```bash
cd scripts

# Fetch tasks from API
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json

# Analyze tasks and create estimates
python3 analyze_tasks.py
```

**Output:**
- Creates `task_estimates.json` with ACTUAL task names and estimates
- Shows analysis summary

**Example Output:**
```
ANALYSIS SUMMARY
═══════════════════════════════════════════════════════════════

Total tasks analyzed: 147
Estimates from TeamGantt: 23
Estimates calculated: 124
Total project hours: 1,847.5h

Sample task estimates:
Task Name                                     Type       Est.     Source       Duration
─────────────────────────────────────────────────────────────────────────────────────
Suspension Design Review                      task       20.0h    calculated      14d
Brake System Integration                      task       15.5h    teamgantt       10d
Vehicle Testing Preparation                   task       12.0h    calculated       8d
...

✅ Task estimates saved to: scripts/task_estimates.json
```

---

### **Step 2: Review & Adjust (Optional)**

Open `task_estimates.json` and manually adjust any estimates:

```bash
nano scripts/task_estimates.json
```

**File Structure:**
```json
{
  "metadata": {
    "project_id": 4452374,
    "generated_at": "2024-10-15T10:30:00",
    "total_tasks": 147,
    "total_estimated_hours": 1847.5
  },
  "tasks": {
    "12345": {
      "name": "Suspension Design Review",
      "type": "task",
      "estimated_hours": 20.0,          ← Edit this if needed
      "source": "calculated",
      "confidence": "medium",
      "duration_days": 14,
      "start_date": "2024-10-01",
      "end_date": "2024-10-14",
      "assigned_to": ["Alice", "Bob"]
    },
    "12346": {
      "name": "Brake System Integration",
      "estimated_hours": 15.5,          ← Or this
      ...
    }
  }
}
```

**Why adjust?**
- You know some tasks are more complex than estimated
- You want to prioritize certain tasks with more hours
- The calculation seems off for specific tasks

---

### **Step 3: Populate Hours**

Now run the hour population with the estimates:

```bash
# Update user roles first
nano scripts/user_roles.json

# DRY RUN to preview
python3 populate_actual_hours.py
```

**The script will:**
- ✅ Load estimates from `task_estimates.json`
- ✅ Use those estimates to weight hour distribution
- ✅ Show you the results before executing

**Example Output:**
```
Loading task estimates...
  ✓ Loaded estimates for 147 tasks

User: Alice (Role: member)
  ✓ 24 weeks active, 195.0h total

Week: Oct 14, 2024
  Total: 10h
  Tasks:
    • Suspension Design (20h est) → 44% → 4.4h
    • Testing Prep (15h est) → 33% → 3.3h
    • Documentation (10h est) → 22% → 2.2h
```

**If happy with preview:**
```bash
# Edit script to execute
nano populate_actual_hours.py
# Change: DRY_RUN = False

# Run for real
python3 populate_actual_hours.py
```

---

## 📊 **What Gets Created:**

### **`task_estimates.json`** (Step 1)
```
✓ ACTUAL task names (not placeholders!)
✓ Task IDs from your project
✓ Estimated hours for each task
✓ Source (TeamGantt vs calculated)
✓ Confidence level
✓ Duration, dates, assignments
✓ Can be manually edited
```

### **Time Entries in TeamGantt** (Step 3)
```
✓ Actual hour entries for each user
✓ Distributed across their assigned tasks
✓ Weighted by task complexity
✓ Realistic time blocks (Mon-Fri, 2-8h/day)
```

---

## 🔄 **When to Re-Run:**

### **Re-run Step 1 (analyze_tasks.py) when:**
- ✅ New tasks added to project
- ✅ Task dates changed significantly
- ✅ You want to refresh estimates
- ✅ TeamGantt estimated_hours updated

### **Re-run Step 3 (populate_actual_hours.py) when:**
- ✅ Ready to populate hours after reviewing estimates
- ✅ Want to regenerate with different user roles
- ✅ Need to repopulate for new time period

---

## 📁 **File Dependencies:**

```
Workflow:
┌─────────────────────────────────────────────────────────┐
│  1. fetch_teamgantt_data.sh                             │
│     └─> Creates: data/children_flat_*.json              │
│                                                          │
│  2. analyze_tasks.py                                    │
│     ├─ Reads: /tmp/test_project_tasks.json             │
│     └─> Creates: task_estimates.json ⭐                 │
│                                                          │
│  3. populate_actual_hours.py                            │
│     ├─ Reads: task_estimates.json ⭐                    │
│     ├─ Reads: user_roles.json                           │
│     ├─ Reads: academic_calendar.json                    │
│     └─> Creates: Time entries in TeamGantt             │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 **Key Benefits:**

### **Before (Placeholders):**
```python
# Task weighting was calculated on-the-fly
# No visibility into what estimates were used
# Hard to adjust without editing code
```

### **After (Actual Tasks in File):**
```json
{
  "12345": {
    "name": "Suspension Design Review",  ← ACTUAL task name!
    "estimated_hours": 20.0,              ← Can edit manually!
    "assigned_to": ["Alice", "Bob"]       ← See assignments!
  }
}
```

**Benefits:**
- ✅ See all tasks and estimates in one file
- ✅ Manually adjust any estimate before populating
- ✅ Source of truth that persists
- ✅ Can review and discuss with team
- ✅ No placeholders - actual project tasks!

---

## 🎯 **Quick Commands:**

```bash
# Full workflow from scratch:
cd scripts

# Step 1: Analyze
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
python3 analyze_tasks.py

# Step 2: Review (optional)
nano task_estimates.json

# Step 3: Populate (dry run)
nano user_roles.json  # Update user names
python3 populate_actual_hours.py

# Step 3b: Populate (for real)
# Edit script: DRY_RUN = False
python3 populate_actual_hours.py
```

---

## ✅ **Checklist:**

Before running:
- [ ] `.env` file has API credentials
- [ ] Fetched latest tasks from TeamGantt
- [ ] Copied tasks to `/tmp/test_project_tasks.json`
- [ ] Ran `analyze_tasks.py` (creates task_estimates.json)
- [ ] Reviewed/edited `task_estimates.json` if needed
- [ ] Updated `user_roles.json` with actual team names
- [ ] Ran dry run to preview
- [ ] Changed `DRY_RUN = False` when ready

---

**This workflow gives you full control with actual task data!** 🚀
