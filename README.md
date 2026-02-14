# R2Y5 TeamGantt Project

This folder contains tools and reports for managing the R2Y5 project in TeamGantt.

## 📁 Folder Structure

```
Autoronto/
├── PROJECT_STATUS_REPORT.html    # ⭐ Main status report (open in browser)
├── PROJECT_STATUS_REPORT.md      # Markdown version of report
├── .env                           # API credentials (DO NOT COMMIT)
├── .gitignore                    # Git ignore rules
├── README.md                      # This file
├── data/                          # Exported project data
│   ├── teamgantt_export_4336931.csv
│   ├── children_flat_4336931.json
│   ├── children_hierarchical_4336931.json
│   ├── project_4336931.json
│   ├── projects.json
│   └── export_job.json
└── scripts/                       # Automation scripts
    ├── fetch_teamgantt_data.sh    # Export data from TeamGantt API
    └── analyze_teamgantt.py       # Analyze and generate reports
```

## 🚀 Quick Start

### View the Report
Simply open **PROJECT_STATUS_REPORT.html** in your browser.

### Export Fresh Data
```bash
./scripts/fetch_teamgantt_data.sh
```
(Uses credentials from `.env` file)

### Generate Updated Report
```bash
python3 scripts/analyze_teamgantt.py
```

## 🔧 Setup

1. **API Token:** Update `.env` with your TeamGantt API token
2. **Dependencies:** Run `pip3 install pandas` (if needed)

## 📊 Current Status (Jan 25, 2026)

- **Progress:** 42.8% complete
- **Hours Logged:** 811 hours
- **Tasks:** 127 across 18 teams
- **Critical Issues:** 
  - ❌ 100% of tasks missing hour estimates
  - ❌ Only 1.6% have dependencies
  - ⚠️ 3DOD: 106.5h logged but 0% progress shown

## 🎯 Next Steps

1. Add hour estimates to all 127 tasks
2. Update progress for teams with logged hours
3. Add task dependencies for critical path
4. Review resource allocation for low-progress teams

---

**Questions?** Contact project management or see TeamGantt documentation.
# Autoronto
