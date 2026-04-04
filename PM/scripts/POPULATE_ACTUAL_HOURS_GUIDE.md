# Populate Actual Hours - Role-Based Guide

This script populates **actual hours** (time entries) in TeamGantt based on realistic student workloads and UofT academic calendar.

---

## 🎯 **What It Does:**

- **NO estimated hours** (leaves them empty)
- **Role-based sampling**: Each user gets hours based on their role (Chad/TD/Lead/Member)
- **Academic calendar aware**: Adjusts for reading weeks, study weeks, exams
- **Week-by-week allocation**: Distributes hours across user's assigned tasks per week
- **TD overhead tracking**: Creates coordination tasks for Technical Directors
- **Realistic time blocks**: 2-8h per day, Monday-Friday only

---

## 🚀 **Quick Start:**

### **1. Update User Roles**

Edit `user_roles.json` with your actual team member names from TeamGantt:

```bash
nano scripts/user_roles.json
```

```json
{
  "role_mapping": {
    "John Doe": "chad_phd",      ← Update with real names
    "Jane Smith": "lead",
    "Bob Wilson": "td",
    "Alice Brown": "member"
  },
  
  "branch_mapping": {
    "Vehicle Systems": "Bob Wilson",  ← TD for each branch
    "Autonomous": "Jane Smith"
  },
  
  "quit_users": []                    ← Add names of people who quit
}
```

### **2. Fetch Project Data**

```bash
cd scripts
./fetch_teamgantt_data.sh
```

### **3. Prepare Task File**

```bash
cp ../data/children_flat_<PROJECT_ID>.json /tmp/test_project_tasks.json
```

### **4. Run DRY RUN**

```bash
python3 populate_actual_hours.py
```

**Output:**
```
User: Chad (Role: chad_phd)
  ✓ 24 weeks active, 288.0h total

User: Bob Wilson (Role: td)
  ✓ 24 weeks active, 276.0h total
    ├─ Overhead: 103.5h (37.5%)
    └─ Tasks: 172.5h

SUMMARY
User                      Role         Total Hours  Weeks   Avg/Week
Chad                      chad_phd          288.0h     24      12.0h
Bob Wilson                td                276.0h     24      11.5h
Jane Smith                lead              246.0h     24      10.3h
Alice Brown               member            195.0h     24       8.1h

Total time blocks: 487
```

### **5. Execute for Real**

Edit the script:

```bash
nano populate_actual_hours.py
```

Change line 34:
```python
DRY_RUN = False  # Set to False to actually execute
```

Run again:
```bash
python3 populate_actual_hours.py
```

---

## 📊 **Role Distributions:**

| Role | Hours/Week | Range | Description |
|------|------------|-------|-------------|
| **Chad (PhD)** | 12h | 9-15h | Consistent year-round, PhD schedule |
| **TD** | 12h | 9-15h | Same as Chad + 37.5% overhead |
| **Lead** | 10.5h | 8-13h | Team leadership role |
| **Member** | 8.5h | 7-10h | Baseline for all members |
| **Inactive** | 3h | 0-6h | Struggling/losing interest |
| **Quit** | 0h | 0h | No contribution |

---

## 📅 **Academic Calendar Modifiers:**

| Period | Multiplier | Effect |
|--------|------------|--------|
| **Normal Semester** | 1.0× | Standard hours |
| **Reading Week** | 1.5× | More time for project work |
| **Study Week** | 0.5× | Studying for exams |
| **Exam Week** | 0.3× | Minimal project work |
| **Summer** | 1.3× | Increased availability |

**Exception**: PhD students (Chad) are NOT affected by reading/study/exam weeks, only slight summer boost.

---

## 🔧 **TD Overhead:**

Technical Directors get **37.5% of their time** allocated to a coordination task:

```
TD: Bob Wilson (12h/week)
├── 4.5h → "Vehicle Systems - TD Coordination & Oversight"
│          (Cross-team meetings, reviews, integration)
└── 7.5h → Distributed across assigned tasks
```

---

## 📋 **How Hours Are Distributed:**

### **For Each Week:**

1. **Sample total hours** for user (based on role + calendar modifier)
2. **Get user's tasks** for that week (tasks with overlapping dates)
3. **If TD**: Allocate 37.5% to overhead, rest to tasks
4. **Calculate task weights** based on task size/complexity:
   - Uses `estimated_hours` from TeamGantt if available
   - Falls back to `duration × 2h/day` if no estimate
   - Bigger tasks get proportionally more hours
5. **Distribute hours** across tasks using weights
6. **Create time blocks** (2-8h per day, Mon-Fri)

### **Example:**

```
Week: Oct 14, 2024 (Normal week)
User: Alice (Member)

1. Sample: 10h (sampled from mean=8.5, σ=0.75)

2. Tasks this week:
   - Task A: "Suspension Design" (20h estimated)
   - Task B: "Testing Prep" (15h estimated)
   - Task C: "Documentation" (10h estimated)

3. Calculate weights by task size:
   Total estimated: 20 + 15 + 10 = 45h
   
   Weights:
   - Task A: 20/45 = 44%
   - Task B: 15/45 = 33%
   - Task C: 10/45 = 22%

4. Distribute Alice's 10h using weights:
   - Task A: 10h × 44% = 4.4h (bigger task, more time)
   - Task B: 10h × 33% = 3.3h
   - Task C: 10h × 22% = 2.2h (smaller task, less time)

5. Create time blocks:
   - Mon: Task A, 9am-2pm (4.4h)
   - Tue: Task B, 10am-1pm (3.3h)
   - Wed: Task C, 1pm-3pm (2.2h)
   
   Total: 10h ✅ (matches Alice's weekly allocation)
```

---

## 🎯 **Example Semester:**

```
Fall 2024 (15 weeks): Member Alice

Week           Period          Base    Modifier  Final   
Sep 9          Normal          8.7h    1.0×      8.7h    
Sep 16         Normal          9.1h    1.0×      9.1h    
Oct 28         Reading Week    8.3h    1.5×      12.5h   ✨ Boost
Dec 9          Study Week      8.5h    0.5×      4.3h    📚 Studying
Dec 16         Exam Week       8.8h    0.3×      2.6h    📝 Exams

Total: ~122h over 15 weeks (8.1h/week average)
```

---

## 📂 **Configuration Files:**

### **`user_roles.json`**
Maps users to roles and branches

### **`academic_calendar.json`**
UofT calendar with reading weeks, study weeks, exams

### **`.env`**
API credentials:
```bash
TEAMGANTT_API_KEY=your_token_here
TEAMGANTT_PROJECT_ID=4452374
```

---

## ⚙️ **Customization:**

### **Adjust Role Hours:**

Edit the script (lines 46-79):

```python
ROLE_DISTRIBUTIONS = {
    'member': {
        'mean': 8.5,      ← Change this
        'std_dev': 0.75,  ← Or this
        ...
    }
}
```

### **Adjust TD Overhead:**

Edit line 54:

```python
'overhead_percentage': 0.375,  # 37.5% → change to 0.5 for 50%
```

### **Adjust Task Distribution:**

Currently uses **size-based weighting** (bigger tasks get more hours).

The weighting algorithm:
1. Check if task has `estimated_hours` in TeamGantt → use that
2. If not, calculate: `duration_days × 2h/day`
3. Weight = `task_estimate / total_of_all_estimates`

To use **equal weighting** instead, modify `calculate_task_weights()` function (line 231):

```python
def calculate_task_weights(tasks):
    """Equal weight for all tasks."""
    if not tasks:
        return {}
    weight = 1.0 / len(tasks)
    return {task['id']: weight for task in tasks}
```

---

## 🐛 **Troubleshooting:**

### **"Task file not found"**
```bash
# Make sure you copied the tasks file:
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
```

### **"TEAMGANTT_API_KEY not found"**
```bash
# Create .env file:
cp .env.example .env
nano .env
# Add your API key
```

### **"No tasks found for user"**
- Check that user names in `user_roles.json` EXACTLY match TeamGantt
- Check that tasks have resource assignments in TeamGantt

### **Hours seem wrong**
- Review the SUMMARY output
- Check role assignments in `user_roles.json`
- Verify calendar modifiers in output

---

## 📊 **Output Files:**

- **`/tmp/actual_hours_population_plan.json`**: Full dry run plan with all time blocks
- Console output: Summary of hours by user and sample time blocks

---

## 🔄 **Workflow:**

```bash
# 1. Update config
nano scripts/user_roles.json

# 2. Fetch data
cd scripts
./fetch_teamgantt_data.sh
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json

# 3. Dry run
python3 populate_actual_hours.py

# 4. Review output, adjust if needed

# 5. Execute
# (Edit script: DRY_RUN = False)
python3 populate_actual_hours.py

# 6. Verify in TeamGantt
open https://app.teamgantt.com/projects/4452374
```

---

## ✅ **Key Features:**

- ✅ **10h/week baseline** for members (7-10h range)
- ✅ **Role hierarchy**: Chad=TD > Lead > Member
- ✅ **Academic calendar aware** (reading/study/exam weeks)
- ✅ **PhD schedule** for Chad (not affected by undergrad calendar)
- ✅ **TD overhead** (37.5% coordination time)
- ✅ **Realistic time blocks** (Mon-Fri, 2-8h/day)
- ✅ **DRY RUN mode** (preview before executing)

---

**Questions?** See full implementation in `populate_actual_hours.py`

**Last Updated**: February 14, 2026
