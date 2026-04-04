# ✅ Hour Population System - Complete

**Created**: February 14, 2026  
**Status**: ✅ Ready for Testing

---

## 🎯 **What Was Built:**

A **3-step system** to populate realistic actual hours in TeamGantt based on:
- Student role distributions (Chad/TD/Lead/Member)
- UofT academic calendar (reading/study/exam weeks)
- Task complexity weighting (from analyzed estimates)

---

## 📊 **The 3-Step Process:**

### **Step 1: Analyze Tasks** (`analyze_tasks.py`)

**Purpose:** Pull tasks from API and create weighting baseline

**What it does:**
- Fetches all tasks from project
- Estimates hours needed based on:
  - TeamGantt's `estimated_hours` (if set)
  - Task duration × 2h/day (if not set)
  - Keyword analysis (design/report/meeting/etc)
- Saves to `task_estimates.json` with **ACTUAL task names**

**Output:** `task_estimates.json`
```json
{
  "tasks": {
    "12345": {
      "name": "Suspension Design Review",
      "estimated_hours": 20.0,
      "source": "calculated",
      "duration_days": 14,
      "assigned_to": ["Alice", "Bob"]
    }
  }
}
```

---

### **Step 2: Review & Edit** (Manual)

**Purpose:** Human review of task estimates

**What you do:**
- Open `task_estimates.json`
- Manually adjust any `estimated_hours` values
- Based on your knowledge of task complexity

**Why this matters:**
- Some tasks more complex than calculated
- Can prioritize important deliverables
- Source of truth for all weighting

---

### **Step 3: Populate Hours** (`populate_actual_hours.py`)

**Purpose:** Distribute hours to users based on roles and calendar

**What it does:**
- FOR EACH user → FOR EACH week:
  1. Sample weekly hours from role distribution
  2. Apply calendar modifier (reading/exam weeks)
  3. Get user's tasks for this week
  4. Load estimates from `task_estimates.json`
  5. Weight tasks by estimates (big tasks get more hours)
  6. Distribute user's weekly hours across tasks
  7. Create realistic time blocks (Mon-Fri, 2-8h/day)

**Output:** Time entries in TeamGantt

---

## 👥 **Role Distributions:**

| Role | Mean | Range | Calendar Type | Special |
|------|------|-------|---------------|---------|
| **Chad (PhD)** | 12h | 9-15h | PhD (year-round) | Not affected by reading/exam weeks |
| **TD** | 12h | 9-15h | Undergrad | 37.5% overhead for coordination |
| **Lead** | 10.5h | 8-13h | Undergrad | - |
| **Member** | 8.5h | 7-10h | Undergrad | Baseline |
| **Inactive** | 3h | 0-6h | Undergrad | Below baseline |

---

## 📅 **UofT Academic Calendar:**

### **Fall 2024:**
- Reading Week: Oct 28 - Nov 1 (1.5×)
- Study Week: Dec 9 - 13 (0.5×)
- Exam Period: Dec 16 - 20 (0.3×)

### **Winter 2025:**
- Reading Week: Feb 17 - 21 (1.5×)
- Study Week: Apr 7 - 11 (0.5×)
- Exam Period: Apr 14 - 25 (0.3×)

### **Summer 2025:**
- May 5 - Aug 31 (1.3× for undergrads, 1.2× for PhD)

---

## 📊 **Task Weighting System:**

### **Example:**

```
User: Alice (Member, 10h this week)

Tasks from task_estimates.json:
  • Task A: "Suspension Design" (20h estimated)
  • Task B: "Testing Prep" (15h estimated)
  • Task C: "Documentation" (10h estimated)

Weights:
  Total: 20 + 15 + 10 = 45h
  
  Task A: 20/45 = 44% → 10h × 44% = 4.4h
  Task B: 15/45 = 33% → 10h × 33% = 3.3h
  Task C: 10/45 = 22% → 10h × 22% = 2.2h

Time Blocks Created:
  Monday:    Task A, 9am-2pm (4.4h)
  Tuesday:   Task B, 10am-1pm (3.3h)
  Wednesday: Task C, 1pm-3pm (2.2h)
  
Total: 10h ✅ (matches Alice's weekly allocation)
```

---

## 🔧 **Scripts Created:**

| Script | Purpose | Output |
|--------|---------|--------|
| **`fetch_teamgantt_data.sh`** | Pull tasks from API | `data/*.json` |
| **`analyze_tasks.py`** ⭐ | Analyze tasks, create estimates | `task_estimates.json` |
| **`populate_actual_hours.py`** ⭐ | Populate hours using estimates | Time entries in TeamGantt |

---

## 📁 **Configuration Files:**

| File | Purpose | Format |
|------|---------|--------|
| **`.env`** | API credentials | `TEAMGANTT_API_KEY=...` |
| **`user_roles.json`** | User→role mapping | JSON |
| **`academic_calendar.json`** | UofT calendar | JSON |
| **`task_estimates.json`** | Task complexity estimates | JSON (generated) |

---

## 📚 **Documentation Files:**

| File | Description |
|------|-------------|
| **`WORKFLOW_GUIDE.md`** | Complete step-by-step workflow |
| **`POPULATE_ACTUAL_HOURS_GUIDE.md`** | Detailed script reference |
| **`TASK_WEIGHTING_EXPLAINED.md`** | How task weighting works |
| **`README_POPULATE_HOURS.md`** | Quick reference |
| **`HOUR_POPULATION_COMPLETE.md`** | This summary |

---

## 🚀 **Quick Start:**

```bash
# 1. Analyze tasks (creates task_estimates.json)
cd scripts
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
python3 analyze_tasks.py

# 2. Review estimates (optional)
nano task_estimates.json

# 3. Update user roles
nano user_roles.json

# 4. Populate hours (dry run)
python3 populate_actual_hours.py

# 5. Execute for real
# (Edit script: DRY_RUN = False)
python3 populate_actual_hours.py
```

---

## ✅ **Key Features:**

### **1. No Placeholders**
- ✅ `task_estimates.json` has ACTUAL task names from your project
- ✅ Task IDs match your TeamGantt project
- ✅ Can see exactly which tasks and their estimates

### **2. Reviewable**
- ✅ Can review all estimates before populating
- ✅ Can manually adjust any task's estimated_hours
- ✅ Human-in-the-loop approval

### **3. Realistic Student Workloads**
- ✅ 7-10h/week for members (baseline)
- ✅ 8-13h/week for leads
- ✅ 9-15h/week for TD and Chad
- ✅ Adjusted for reading weeks, exams, summer

### **4. Calendar-Aware**
- ✅ Reading weeks: 1.5× hours
- ✅ Study weeks: 0.5× hours
- ✅ Exam weeks: 0.3× hours
- ✅ PhD students: consistent year-round

### **5. TD Overhead Tracking**
- ✅ 37.5% of TD hours go to coordination
- ✅ Creates separate overhead task entries
- ✅ Visible in dashboard

---

## 📊 **Semester Example:**

```
Fall 2024 Totals (15 weeks):

Role         Avg/Week    Total       Notes
────────────────────────────────────────────────────────────
Chad (PhD)   12.0h       180h       Consistent year-round
TD           11.5h       172h       Includes 37.5% overhead
Lead         10.0h       150h       Above baseline
Member        8.1h       122h       Close to 10h target
Inactive      2.9h        43h       Below baseline
```

---

## 🎯 **What Makes This Better:**

### **vs Equal Split:**
```
❌ Old: Each task gets 33% regardless of size
✅ New: Tasks weighted by complexity (big = more hours)
```

### **vs Hardcoded Estimates:**
```
❌ Old: Estimates in code, hard to change
✅ New: Estimates in JSON file, easy to review/edit
```

### **vs Placeholders:**
```
❌ Old: "Task A", "Task B", "Task C" in examples
✅ New: "Suspension Design Review", "Brake Integration" (actual tasks!)
```

---

## 🔄 **Update Workflow:**

If tasks change in TeamGantt:

```bash
# Re-analyze tasks
cd scripts
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
python3 analyze_tasks.py

# Review new estimates
nano task_estimates.json

# Re-populate if needed
python3 populate_actual_hours.py
```

---

## 📞 **Files to Share with Team:**

**For developers:**
- `WORKFLOW_GUIDE.md` - Complete workflow
- `user_roles.json` - Update with their names
- `task_estimates.json` - Review task estimates

**For understanding:**
- `TASK_WEIGHTING_EXPLAINED.md` - How weighting works
- `README_POPULATE_HOURS.md` - Quick reference

---

## ✅ **Ready for Testing!**

All scripts are complete and documented. The system:
- ✅ Pulls ACTUAL tasks from your project
- ✅ Stores estimates locally for review
- ✅ Uses those estimates for realistic weighting
- ✅ Distributes hours based on student roles
- ✅ Respects UofT academic calendar
- ✅ Creates realistic time blocks

**Next step:** Run `analyze_tasks.py` to pull your actual tasks! 🚀
