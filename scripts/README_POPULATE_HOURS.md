# 📊 Hour Population Scripts - Quick Reference

## 🎯 **Two Scripts Available:**

### **1. `populate_test_project_hours.py` (ORIGINAL)**
- ✅ Populates **estimated** hours based on task keywords
- ✅ Calculates **actual** hours from estimates × progress
- ❌ **NOT** role-based
- ❌ **NOT** calendar-aware

### **2. `populate_actual_hours.py` (NEW - ROLE-BASED)** ⭐
- ❌ **Skips** estimated hours (leaves empty)
- ✅ Populates **actual** hours based on user roles
- ✅ **Role-based** sampling (Chad/TD/Lead/Member)
- ✅ **UofT calendar-aware** (reading weeks, exams)
- ✅ **TD overhead** tracking (37.5% coordination)
- ✅ **Week-by-week** allocation

---

## 🚀 **Recommended: Use New Script (3-Step Process)**

### **Step 1: Analyze Tasks**
```bash
cd scripts
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
python3 analyze_tasks.py
```
**Creates:** `task_estimates.json` with ACTUAL task names and estimates

### **Step 2: Review & Edit (Optional)**
```bash
nano scripts/task_estimates.json
# Manually adjust task estimates if needed
```

### **Step 3: Populate Hours**
```bash
nano scripts/user_roles.json  # Update with real names
python3 populate_actual_hours.py  # Dry run
# (Edit script: DRY_RUN = False)
python3 populate_actual_hours.py  # Execute
```

**Full guides:**
- `WORKFLOW_GUIDE.md` - Complete 3-step process
- `TASK_WEIGHTING_EXPLAINED.md` - How task weighting works
- `POPULATE_ACTUAL_HOURS_GUIDE.md` - Detailed reference

---

## 📋 **Quick Comparison:**

| Feature | Old Script | New Script |
|---------|------------|------------|
| Estimated hours | ✅ Yes | ❌ No |
| Actual hours | ✅ Yes | ✅ Yes |
| Role-based | ❌ No | ✅ Yes |
| Calendar-aware | ❌ No | ✅ Yes |
| TD overhead | ❌ No | ✅ Yes |
| Student-realistic | ❌ No | ✅ Yes (7-15h/week) |

---

## 🎓 **Role Distributions (New Script):**

```
Chad (PhD):   12h/week (9-15h) - consistent year-round
TD:           12h/week (9-15h) - includes 37.5% overhead
Lead:         10.5h/week (8-13h) - team leadership
Member:       8.5h/week (7-10h) - baseline for all
Inactive:     3h/week (0-6h) - struggling
```

---

## 📅 **Calendar Modifiers:**

```
Reading Week:  1.5× (more time for project)
Study Week:    0.5× (preparing for exams)
Exam Week:     0.3× (minimal project work)
Summer:        1.3× (increased availability)
Normal:        1.0× (standard semester)
```

**Exception**: PhD students (Chad) NOT affected by reading/study/exam weeks

---

## 📂 **Files:**

- **`populate_actual_hours.py`** - Main script (role-based) ⭐
- **`populate_test_project_hours.py`** - Original script (keyword-based)
- **`user_roles.json`** - User→role mapping (EDIT THIS!)
- **`academic_calendar.json`** - UofT calendar
- **`POPULATE_ACTUAL_HOURS_GUIDE.md`** - Detailed guide
- **`INSTRUCTIONS_POPULATE_HOURS.md`** - Original script guide

---

**Use the NEW script for realistic student workloads! 🚀**
