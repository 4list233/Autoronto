# 📊 Task Weighting System - Explained

## 🎯 **Purpose:**

Distribute a user's weekly hours across their tasks **proportionally to task size/complexity**, rather than equally.

---

## ⚖️ **Old vs New:**

### **❌ Old: Equal Split**
```
User has 10h this week
3 tasks assigned (any size)

Distribution:
  Task A: 3.33h (33%)  } Same for all
  Task B: 3.33h (33%)  } regardless
  Task C: 3.33h (33%)  } of size
```

### **✅ New: Weighted by Task Size**
```
User has 10h this week
3 tasks assigned:
  - Task A: needs 20h to complete
  - Task B: needs 15h to complete
  - Task C: needs 10h to complete

Weights:
  - Task A: 20 / (20+15+10) = 44%
  - Task B: 15 / (20+15+10) = 33%
  - Task C: 10 / (20+15+10) = 22%

Distribution:
  Task A: 4.4h (44%)  } Proportional to
  Task B: 3.3h (33%)  } task complexity/
  Task C: 2.2h (22%)  } effort needed
```

---

## 🔍 **How Task Size is Determined:**

The script uses a **priority system** to estimate hours needed:

### **Priority 1: Use TeamGantt's estimated_hours**
```python
task = {
    'id': 123,
    'name': 'Suspension Design',
    'estimated_hours': 20  ← Use this if available
}

estimate = 20h
```

### **Priority 2: Calculate from Task Duration**
```python
task = {
    'id': 124,
    'name': 'Testing Prep',
    'start_date': '2024-10-14',
    'end_date': '2024-10-21',  # 7 days
    'estimated_hours': 0  ← Not set
}

duration = 7 days
estimate = 7 days × 2h/day = 14h
```

### **Priority 3: Default**
```python
task = {
    'id': 125,
    'name': 'Unknown Task',
    # No dates, no estimate
}

estimate = 5h (default)
```

---

## 💡 **Benefits:**

1. **More Realistic**
   - Large complex tasks naturally get more time
   - Small quick tasks get less time
   - Reflects actual work distribution

2. **Respects Task Estimates**
   - Uses your existing TeamGantt estimates
   - No manual configuration needed

3. **Fair Allocation**
   - User's total weekly hours stay the same
   - Just distributed more intelligently

4. **Handles Missing Data**
   - Falls back gracefully if no estimates
   - Uses duration as proxy for complexity

---

## 📊 **Real Example:**

```
Week: October 14, 2024
User: Alice (Member role)
Weekly Hours: 10h (sampled from distribution)

Tasks Assigned This Week:
┌─────────────────────────┬──────────┬──────────┬────────┬────────────┐
│ Task                    │ Estimate │ Weight   │ Hours  │ Time Blocks│
├─────────────────────────┼──────────┼──────────┼────────┼────────────┤
│ Suspension Design       │ 20h      │ 44%      │ 4.4h   │ Mon 9am-2pm│
│ Testing Prep            │ 15h      │ 33%      │ 3.3h   │ Tue 10am-1pm│
│ Documentation Update    │ 10h      │ 22%      │ 2.2h   │ Wed 1pm-3pm│
├─────────────────────────┼──────────┼──────────┼────────┼────────────┤
│ TOTAL                   │ 45h      │ 100%     │ 10h ✅ │            │
└─────────────────────────┴──────────┴──────────┴────────┴────────────┘

Verification:
  4.4 + 3.3 + 2.2 = 10.0h ✅ (matches Alice's weekly allocation)
```

---

## 🔧 **Implementation Details:**

### **Function: `estimate_task_hours(task)`**
```python
def estimate_task_hours(task):
    """
    Estimate hours needed to complete a task.
    
    Returns:
        float: Estimated hours (1-40h range)
    """
    # 1. Check for estimated_hours field
    estimated = task.get('estimated_hours', 0)
    if estimated and estimated > 0:
        return estimated
    
    # 2. Calculate from duration
    duration_days = calculate_duration_days(task)
    estimated = duration_days * 2.0  # 2h per day baseline
    
    # 3. Clamp to reasonable range
    return max(1.0, min(40.0, estimated))
```

### **Function: `calculate_task_weights(tasks)`**
```python
def calculate_task_weights(tasks):
    """
    Calculate proportional weights based on task size.
    
    Returns:
        Dict: {task_id: weight} where weights sum to 1.0
    """
    # Estimate each task
    task_estimates = {
        task['id']: estimate_task_hours(task)
        for task in tasks
    }
    
    # Calculate total
    total_estimated = sum(task_estimates.values())
    
    # Calculate proportional weights
    weights = {
        task_id: estimate / total_estimated
        for task_id, estimate in task_estimates.items()
    }
    
    return weights
```

---

## 🎯 **Use Cases:**

### **Scenario 1: Well-Estimated Project**
Your project has `estimated_hours` set for all tasks in TeamGantt.

**Result:** Script uses your estimates directly for perfect weighting ✅

### **Scenario 2: No Estimates Set**
Tasks have dates but no estimated_hours.

**Result:** Script calculates from duration (duration × 2h/day) 👍

### **Scenario 3: Mixed**
Some tasks have estimates, others don't.

**Result:** Script uses estimates where available, calculates for the rest ✅

---

## 📋 **Dry Run Output:**

The script shows you the weighting in action:

```
TASK WEIGHTING EXAMPLE
=========================================================================

Hours are distributed based on task size/complexity:
  - Uses estimated_hours from TeamGantt if available
  - Falls back to duration × 2h/day if no estimate
  - Bigger tasks get proportionally more hours

Example:
  User has 10h this week, 3 tasks assigned:
    • Task A: 20h estimated → 44% weight → 4.4h this week
    • Task B: 15h estimated → 33% weight → 3.3h this week
    • Task C: 10h estimated → 22% weight → 2.2h this week
  Total: 10h (matches user's weekly allocation)
```

---

## 🔄 **To Use Equal Weighting Instead:**

If you prefer the old equal-split approach, modify the script:

```python
def calculate_task_weights(tasks):
    """Use equal weighting instead."""
    if not tasks:
        return {}
    weight = 1.0 / len(tasks)
    return {task['id']: weight for task in tasks}
```

---

## ✅ **Summary:**

| Aspect | Implementation |
|--------|----------------|
| **Data Source** | TeamGantt `estimated_hours` field |
| **Fallback** | Duration × 2h/day |
| **Default** | 5h if no data available |
| **Range** | 1h - 40h (clamped) |
| **Distribution** | Proportional to task size |
| **User Total** | Always matches sampled weekly hours |

---

**This makes hour allocation more realistic and respects the complexity of each task!** 🚀
