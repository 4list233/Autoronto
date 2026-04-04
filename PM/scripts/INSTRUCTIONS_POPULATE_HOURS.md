# Instructions: Populating Test Project Hours in TeamGantt

This guide explains how to populate estimated and actual hours for a TeamGantt test project using the provided scripts. You can use this for dry runs or real data population.

⚠️ **IMPORTANT**: This script will modify data in TeamGantt. Always run in DRY RUN mode first!

---

## 1. Prerequisites
- Python 3.8+ and `curl` must be installed
- You have access to the `scripts/` directory in this repo
- TeamGantt API token and project ID (see setup below)

---

## 1.5. Setup .env File

Create a `.env` file in the **project root** (not in scripts/) with your API credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual credentials
nano .env
```

**Add this content:**

```bash
TEAMGANTT_API_KEY=your_actual_api_token_here
TEAMGANTT_PROJECT_ID=4452374
```

**🔒 SECURITY**: 
- The `.env` file is already in `.gitignore` - it will NOT be committed to git
- **NEVER** share your API token with others
- **NEVER** commit `.env` to version control

**Where to find your API token:**
1. Log into TeamGantt
2. Go to Settings → API
3. Generate or copy your API token

---

## 2. Fetch Project Data

Before populating hours, fetch the latest project data from TeamGantt:

```bash
cd scripts
./fetch_teamgantt_data.sh
```

**What happens:**
- Reads API credentials from `.env` file (or prompts if not found)
- Fetches project data from TeamGantt API
- Creates these files in the `data/` directory:
  - `projects.json` - List of all accessible projects
  - `teamgantt_export_<PROJECT_ID>.csv` - Full project export (CSV)
  - `children_flat_<PROJECT_ID>.json` - Flat list of all tasks
  - `children_hierarchical_<PROJECT_ID>.json` - Hierarchical task structure
  - `project_<PROJECT_ID>.json` - Project metadata

**Expected output:**
```
Fetching TeamGantt data...
✅ Projects fetched: 3 projects found
✅ Exporting project 4452374...
✅ Export complete: 47 tasks
✅ All data saved to ../data/
```

### Expected File Structure After Fetch:

```
Autoronto/
├── .env                              # Your API credentials (NOT in git)
├── .env.example                      # Template file (safe to commit)
├── scripts/
│   ├── fetch_teamgantt_data.sh      # Data fetch script
│   ├── populate_test_project_hours.py  # Population script
│   └── INSTRUCTIONS_POPULATE_HOURS.md  # This file
└── data/
    ├── projects.json
    ├── teamgantt_export_4452374.csv
    ├── children_flat_4452374.json
    ├── children_hierarchical_4452374.json
    └── project_4452374.json
```

---

## 3. Prepare Task List for Population

The population script expects a flat list of tasks in `/tmp/test_project_tasks.json`.

**Copy the tasks file:**

```bash
# Replace 4452374 with your actual project ID
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
```

**Verify the file:**

```bash
# Check file exists and has content
ls -lh /tmp/test_project_tasks.json

# Optional: Preview first few tasks
head -n 50 /tmp/test_project_tasks.json
```

---

## 4. Dry Run: Preview Changes

⚠️ **ALWAYS run in DRY RUN mode first!**

The script defaults to DRY RUN mode (no changes made):

```bash
python3 populate_test_project_hours.py
```

**What happens:**
- Loads tasks from `/tmp/test_project_tasks.json`
- Calculates estimated hours based on task keywords
- Calculates actual hours based on progress percentage
- Distributes actual hours into realistic time blocks
- Prints a preview of all changes
- Saves detailed plan to `/tmp/time_population_plan.json`
- **DOES NOT** make any changes to TeamGantt

### Expected Dry Run Output:

```
================================================================================
TeamGantt Test Project - Time Population Script (Option A: Realistic)
================================================================================
Project ID: 4452374
Mode: DRY RUN (preview only)

Loading tasks from /tmp/test_project_tasks.json...
Found 47 tasks/milestones to process

⏭️  Skipping Some Task (already has 5.0h estimated)

================================================================================
PREVIEW OF CHANGES
================================================================================

📊 Summary:
  Tasks to update: 42
  Total estimated hours: 342.5h
  Total actual hours: 198.3h
  Time blocks to create: 87

📋 Sample updates (first 10):
Task Name                                Type       Est.   Actual  Prog.  Blocks
-------------------------------------------------------------------------------------
Project Proposal                         task       10.5h   6.3h    60%      3
Team Meeting                             task        2.0h   2.1h   100%      1
Design Review                            task        7.5h   0.0h     0%      0
Implementation Phase                     task       18.2h  12.4h    68%      5
... and 32 more tasks

⏱️  Sample time blocks (first 5):
  Project Proposal                      | 2026-02-01 | 3.5h
  Project Proposal                      | 2026-02-02 | 2.8h
  Team Meeting                          | 2026-02-03 | 2.1h
  ... and 82 more time blocks

================================================================================

✅ DRY RUN COMPLETE - No changes were made

To execute these changes:
1. Review the preview above
2. Edit this script and set DRY_RUN = False
3. Run the script again

💾 Detailed plan saved to: /tmp/time_population_plan.json
```

**Review the plan file:**

```bash
# View the detailed plan
cat /tmp/time_population_plan.json | head -n 100
```

---

## 5. Execute for Real (Live Update)

⚠️ **WARNING**: This will modify data in TeamGantt! Make sure you've reviewed the dry run output first.

**Steps to execute:**

1. **Open the script in an editor:**
   ```bash
   nano populate_test_project_hours.py
   ```

2. **Find this line** (around line 24):
   ```python
   DRY_RUN = True  # Set to False to actually execute (SAFER DEFAULT)
   ```

3. **Change it to:**
   ```python
   DRY_RUN = False  # Set to False to actually execute (SAFER DEFAULT)
   ```

4. **Save and exit:**
   - In nano: `Ctrl+X`, then `Y`, then `Enter`
   - In vim: `:wq`

5. **Run the script:**
   ```bash
   python3 populate_test_project_hours.py
   ```

**What happens:**
- Phase 1: Updates estimated hours for each task (PATCH requests)
- Phase 2: Creates time blocks for actual hours (POST requests)
- Rate limiting: 0.5s delay between each API call
- Progress indicators show success (✅) or failure (❌) for each task

**Expected live execution output:**

```
================================================================================
TeamGantt Test Project - Time Population Script (Option A: Realistic)
================================================================================
Project ID: 4452374
Mode: LIVE EXECUTION

🚀 EXECUTING UPDATES...
================================================================================

📝 Phase 1: Updating estimated hours...
  [1/42] Updating Project Proposal                           -> 10.5h... ✅
  [2/42] Updating Team Meeting                               -> 2.0h... ✅
  [3/42] Updating Design Review                              -> 7.5h... ✅
  ... (progress continues) ...

✅ Phase 1 complete: 42 updated, 0 failed

⏱️  Phase 2: Creating 87 time blocks...
  [1/87] Project Proposal                       3.5h... ✅
  [2/87] Project Proposal                       2.8h... ✅
  ... (progress continues) ...

✅ Phase 2 complete: 87 created, 0 failed

================================================================================
✅ EXECUTION COMPLETE!

Summary:
  • Estimated hours updated: 42/42
  • Time blocks created: 87

Verify in TeamGantt: https://app.teamgantt.com/projects/4452374
```

6. **Verify in TeamGantt immediately:**
   - Open the link shown in the output
   - Check that tasks have estimated hours
   - Check that time blocks appear for tasks with progress

---

## 6. Verify in TeamGantt

**Log into TeamGantt and verify:**

1. **Check estimated hours:**
   - Open your project
   - Look at task details
   - Verify estimated hours match the dry run preview

2. **Check time blocks:**
   - Go to Time Tracking view
   - Verify time entries were created
   - Check dates and hours are reasonable

3. **Check totals:**
   - Project summary should show total estimated vs actual hours
   - Compare to the script's summary output

---

## 7. Troubleshooting

### "ERROR: TEAMGANTT_API_KEY not found"
**Problem:** Script can't find your API credentials

**Fix:**
```bash
# Make sure .env exists in project root
ls -la .env

# If not, create it
cp .env.example .env
nano .env
# Add your credentials, save, and retry
```

---

### "No such file or directory: .env"
**Problem:** `.env` file doesn't exist

**Fix:**
```bash
# From project root
cp .env.example .env
nano .env
# Add: TEAMGANTT_API_KEY=your_token_here
```

---

### "Permission denied" when running fetch script
**Problem:** Script is not executable

**Fix:**
```bash
chmod +x scripts/fetch_teamgantt_data.sh
```

---

### "API token invalid" or "401 Unauthorized"
**Problem:** Token is incorrect or expired

**Fix:**
1. Log into TeamGantt
2. Go to Settings → API
3. Regenerate your API token
4. Update `.env` file with new token

---

### "Rate limit exceeded"
**Problem:** Too many API calls too quickly

**Fix:**
- The script has built-in delays (0.5s between calls)
- If you still hit limits, edit the script and increase `RATE_LIMIT_DELAY`:
  ```python
  RATE_LIMIT_DELAY = 1.0  # Increase to 1 second
  ```

---

### "Task file not found"
**Problem:** `/tmp/test_project_tasks.json` doesn't exist

**Fix:**
```bash
# Make sure you ran step 2 (fetch data) first
cd scripts
./fetch_teamgantt_data.sh

# Then copy the tasks file (step 3)
cp ../data/children_flat_4452374.json /tmp/test_project_tasks.json
```

---

### Script runs but no changes in TeamGantt
**Problem:** DRY_RUN is still set to True

**Fix:**
- Make sure you changed `DRY_RUN = True` to `DRY_RUN = False` in the script
- Save the file before running
- Look for "Mode: LIVE EXECUTION" in the output (not "DRY RUN")

---

## 8. Important Notes

✅ **Best Practices:**
- **ALWAYS** run in DRY RUN mode first
- Review the preview output carefully
- Only set `DRY_RUN = False` when you're ready to commit changes
- Verify changes in TeamGantt immediately after execution
- Keep backups of important project data

🔒 **Security:**
- **NEVER** share your API token with others
- **NEVER** commit `.env` to git (already in `.gitignore`)
- The `.env` file contains sensitive credentials
- Rotate your API token regularly

⚙️ **Technical:**
- The script respects rate limits (0.5s delay between calls)
- Time blocks are distributed across working days (Mon-Fri)
- Tasks at 0% progress get no actual hours/time blocks
- Estimates are based on task keywords and duration
- Front-loaded work distribution (more realistic)

🔄 **Repeating:**
- You can repeat the dry run as many times as needed
- The script skips tasks that already have estimates (line 202)
- To recalculate all estimates, comment out lines 202-204

---

## 9. How It Works

### Estimation Logic:

The script estimates hours based on task keywords:

| Keyword | Hours Range | Example |
|---------|-------------|---------|
| `proposal` | 8-12h | Project proposals, major deliverables |
| `report` | 15-25h | Reports, documentation |
| `presentation` | 5-8h | Presentations, demos |
| `meeting` | 1-2h | Team meetings |
| `research` | 8-15h | Research tasks |
| `design` | 5-10h | Design work |
| `implementation` | 10-20h | Development, implementation |
| `testing` | 5-10h | Testing, QA |
| `review` | 2-4h | Reviews, feedback |
| `milestone` | 0.5-1h | Milestone coordination |
| (default) | 3-8h | Tasks with no keywords |

### Actual Hours Logic:

- Only calculated for tasks with `progress > 0`
- Formula: `actual = estimated × (progress / 100) × variance`
- Variance: 0.85 - 1.15 (realistic variation)

### Time Block Distribution:

- Distributed across working days (Mon-Fri) only
- Front-loaded (more work at start of task)
- 2-6 hours per day
- No future work (respects current date)
- Random start times (9am-2pm window)

---

## 10. Resources

**TeamGantt API Documentation:**
- https://api.teamgantt.com/v1/docs

**Project Files:**
- `fetch_teamgantt_data.sh` - Fetches data from API
- `populate_test_project_hours.py` - Populates hours and time blocks
- `.env.example` - Template for API credentials
- `INSTRUCTIONS_POPULATE_HOURS.md` - This guide

**Related Dashboard Files:**
- `dashboard/` - Streamlit dashboard for viewing data
- `DEPLOYMENT_GUIDE.md` - How to deploy dashboard
- `TEAMGANTT_TIME_TRACKING_GUIDE.md` - Time tracking guide

---

**For questions or issues, contact the project maintainer or team lead.**

Last Updated: February 14, 2026
