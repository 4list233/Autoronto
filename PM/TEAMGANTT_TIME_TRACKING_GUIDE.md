# TeamGantt Time Tracking API Guide

This guide explains how to update estimated hours and log actual hours for tasks using the TeamGantt REST API.

## Prerequisites

- TeamGantt API Token: `YOUR_TOKEN_HERE`
- Project ID: `4336931`
- project test id: "4452374"
- Base API URL: `https://api.teamgantt.com/v1`

## 1. Update Estimated Hours

Use `PATCH /v1/tasks/{taskId}` to update the estimated hours for a task.

### Request Format

```bash
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"estimated_hours": 2}' \
  "https://api.teamgantt.com/v1/tasks/TASK_ID"
```

### Example

```bash
# Set estimated hours to 2 for task 164600364
curl -X PATCH \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"estimated_hours": 2}' \
  "https://api.teamgantt.com/v1/tasks/164600364"
```

### Response

The task object is returned with updated `estimated_hours` field:

```json
{
  "id": 164600364,
  "name": "Advisor presentation run-through",
  "estimated_hours": 2,
  "actual_hours": 0,
  ...
}
```

## 2. Log Actual Hours (Time Blocks)

Use `POST /v1/times` to create a time block (time entry) for a task. This is the **correct** way to log actual hours.

### Request Format

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": TASK_ID,
    "start_time": "YYYY-MM-DDTHH:MM:SSZ",
    "end_time": "YYYY-MM-DDTHH:MM:SSZ"
  }' \
  "https://api.teamgantt.com/v1/times"
```

### Example: Log 1 Hour of Work

```bash
# Log 1 hour (9am-10am) for task 164600364 on Jan 28, 2026
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 164600364,
    "start_time": "2026-01-28T09:00:00Z",
    "end_time": "2026-01-28T10:00:00Z"
  }' \
  "https://api.teamgantt.com/v1/times"
```

### Example: Log 3.5 Hours of Work

```bash
# Log 3.5 hours (1pm-4:30pm) for task 164600364
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 164600364,
    "start_time": "2026-01-28T13:00:00Z",
    "end_time": "2026-01-28T16:30:00Z"
  }' \
  "https://api.teamgantt.com/v1/times"
```

### Response

A time block object is created and returned:

```json
{
  "id": 8210761,
  "task_id": 164600364,
  "task_name": "Advisor presentation run-through",
  "start_time": "2026-01-28T09:00:00Z",
  "end_time": "2026-01-28T10:00:00Z",
  "type": "entered",
  "user_id": 14956954,
  "project_id": 4336931,
  ...
}
```

## 3. Verify Task Status

Check the task to see both estimated and actual hours:

```bash
curl -s \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  "https://api.teamgantt.com/v1/tasks/164600364" \
  | python3 -c 'import sys, json; d=json.load(sys.stdin); \
    print("Task:", d["name"]); \
    print("Estimated Hours:", d["estimated_hours"]); \
    print("Actual Hours:", d["actual_hours"])'
```

### Output

```
Task: Advisor presentation run-through
Estimated Hours: 2
Actual Hours: 1
```

## Important Notes

### Time Format
- Always use ISO 8601 format in UTC: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2026-01-28T09:00:00Z` = January 28, 2026 at 9:00 AM UTC

### Hours Calculation
- Actual hours are calculated automatically from the time blocks
- To log 1 hour, set start and end times 1 hour apart
- Multiple time blocks can be created for the same task (they sum up)

### What Doesn't Work
- ❌ `POST /v1/time` (without the 's') - Returns 404
- ❌ `PATCH /v1/tasks/{id}` with `{"actual_hours": 1}` - Ignored
- ❌ `PATCH /v1/resources/{id}` with hours - Returns 404

### What Works
- ✅ `PATCH /v1/tasks/{id}` with `{"estimated_hours": X}` - Updates estimates
- ✅ `POST /v1/times` with time blocks - Logs actual hours

## Finding Task IDs

### From CSV Export

1. Look in `data/teamgantt_export_4336931.csv`
2. Find the WBS number (e.g., `16.2.6`)
3. Cross-reference with JSON data

### From JSON Export

```bash
cat data/children_flat_4336931.json | python3 -c "
import sys, json
data = json.load(sys.stdin)
# Find tasks by name or WBS
for task in data:
    if 'Advisor presentation' in task.get('name', ''):
        print(f\"Task: {task['name']}\")
        print(f\"ID: {task['id']}\")
        print(f\"WBS: {task['wbs']}\")
        print()
"
```

## Quick Reference: Chad Paik's Tasks

| WBS | Task Name | Task ID | Current Status |
|-----|-----------|---------|----------------|
| 1.1.1 | Recruitment for Business Developer | 164600300 | 17.5h actual |
| 1.1.3 | Recruitment for Mechanical Team | 164600302 | 19h actual |
| 1.1.5 | Recruitment for Embedded Systems/Computer Vision | 164600304 | 2h actual |
| 1.16.2.2 | Advisor presentation prep | 164600362 | Milestone |
| 1.16.2.6 | Advisor presentation run-through | 164600364 | 2h est, 1h actual ✅ |

## Batch Operations Example

To update multiple tasks for the same person:

```bash
#!/bin/bash
TOKEN="YOUR_TOKEN_HERE"

# Set estimated hours for multiple tasks
for TASK_ID in 164600300 164600302 164600304; do
  curl -X PATCH \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"estimated_hours": 5}' \
    "https://api.teamgantt.com/v1/tasks/$TASK_ID"
done

# Log 2 hours of work across multiple tasks on the same day
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 164600300,
    "start_time": "2026-01-28T09:00:00Z",
    "end_time": "2026-01-28T11:00:00Z"
  }' \
  "https://api.teamgantt.com/v1/times"
```

## API Documentation Reference

Full API documentation: https://api-docs.teamgantt.com/

Key endpoints:
- Tasks: https://api-docs.teamgantt.com/#tag/tasks
- Time Blocks: https://api-docs.teamgantt.com/#tag/times/operation/createTimeBlock
