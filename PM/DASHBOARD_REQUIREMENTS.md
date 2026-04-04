# Autoronto PM Dashboard Requirements

## Project Overview
**Purpose**: Multi-page PM dashboard for tracking Autoronto's 18-team structure, weekly hour logging (10h members, 13h leads), and WBS-aligned progress monitoring for SAE competition (deadline: June 2026)

**Target Users**: Project Manager, Team Leads (18 teams), Members (70+ students)

**Data Source**: TeamGantt API → cached locally for performance

---

## Core Features

### 1. Weekly Hour Tracking System
- **Default Allocations**:
  - Members: 10 hours/week
  - Leads: 13 hours/week (30% premium)
- **Logging Period**: Weekly on Saturdays for previous Monday-Friday
- **Distribution**: Hours auto-distributed across assigned tasks proportionally to estimated workload
- **Manual Override**: Allow manual hour entry for specific tasks

### 2. Outlier Detection & Alerts
- **Low Hour Contributors** (configurable):
  - Default threshold: < 7 hours/week (70% of expected)
  - Adjustable range: 0-10 hours
  - Flag duration: consecutive weeks below threshold
- **Over-Contributing Members** (configurable):
  - Default threshold: > 15 hours/week for members, > 20 hours/week for leads
  - Adjustable range: 12-30 hours
  - Alert after 2 consecutive weeks above threshold
- **Visual Indicators**: 🔴 red badge for under-contributing, 🟠 orange badge for over-contributing

### 3. Progress Tracking
- Estimate vs Actual hours comparison
- Progress percentage per task (0%, 25%, 50%, 75%, 100%)
- Weighted rollup to team and project levels
- Variance analysis (on-track, at-risk, blocked)

### 4. Role-Based Access
- **PM View**: All teams, all data, configuration controls
- **Lead View**: Own team only, member contributions, outlier alerts
- **Member View**: Own tasks, own hours, team summary

---

## Page Structure

### PAGE 1: Executive Dashboard (Home)
**Purpose**: High-level project health snapshot for PM and stakeholders

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ 🏁 AUTORONTO SAE 2026 - PROJECT OVERVIEW               │
├─────────────────────────────────────────────────────────┤
│ 📅 Days to June Competition: [134]                      │
│ 📅 Days to Winter Workshop: [10] (Feb 17)              │
├─────────────────────────────────────────────────────────┤
│ Project Completion: [43%] ████████░░░░░░░░░░           │
│ Total Hours: 1,234 / 2,500 estimated                   │
├─────────────────────────────────────────────────────────┤
│ Task Status:                                            │
│ ● Complete: 45 (35%)                                    │
│ ● In Progress: 62 (49%)                                 │
│ ● Not Started: 20 (16%)                                 │
│ [Pie Chart Visualization]                               │
├─────────────────────────────────────────────────────────┤
│ 🚨 Critical Alerts:                                     │
│ • 3 teams behind schedule                               │
│ • 8 tasks overdue > 7 days                              │
│ • 12 members below hour threshold this week             │
│ • 3 members over-contributing                           │
├─────────────────────────────────────────────────────────┤
│ Team Health Heatmap (3x6 grid):                         │
│ ┌──────┬──────┬──────┬──────┬──────┬──────┐           │
│ │ 🟢1.1 │ 🟢1.2 │ 🟡1.3 │ 🟢1.4 │ 🟢1.5 │ 🔴1.6 │     │
│ │ 87%  │ 92%  │ 65%  │ 78%  │ 85%  │ 23%  │           │
│ ├──────┼──────┼──────┼──────┼──────┼──────┤           │
│ │ 🟢1.7 │ 🟡1.8 │ 🟢1.9 │ 🟢1.10│ 🟡1.11│ 🟢1.12│     │
│ │ ...                                       │           │
│ └──────┴──────┴──────┴──────┴──────┴──────┘           │
└─────────────────────────────────────────────────────────┘
```

**Metrics**:
- Days to key milestones (Feb 17, June 2026)
- Overall completion % (weighted by estimated hours)
- Total hours logged vs estimated
- Task status distribution
- Critical alerts summary
- 18-team health grid (color-coded, clickable)

**Interactions**:
- Click team card → navigate to Team Detail Page
- Click alerts → navigate to At-Risk Dashboard
- Refresh button to sync latest data

---

### PAGE 2: Team Performance Grid
**Purpose**: Compare all 18 teams side-by-side, identify lagging teams

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ TEAM PERFORMANCE OVERVIEW                               │
│ Sort by: [Progress ▼] | Filter: [All Teams ▼]          │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐ ┌─────────────────────┐        │
│ │ 1.2 Kinematics      │ │ 1.7 Suspension      │        │
│ │ Lead: Jane Smith    │ │ Lead: Bob Johnson   │        │
│ │ ────────────────────│ │ ────────────────────│        │
│ │ Progress: 92% 🟢    │ │ Progress: 85% 🟢    │        │
│ │ Hours: 245/280      │ │ Hours: 189/220      │        │
│ │ Tasks: 12/14 ✓      │ │ Tasks: 8/10 ✓       │        │
│ │ Members: 5 active   │ │ Members: 4 active   │        │
│ │ Status: On Track    │ │ Status: On Track    │        │
│ └─────────────────────┘ └─────────────────────┘        │
│ ┌─────────────────────┐ ┌─────────────────────┐        │
│ │ 1.3 Controls        │ │ 1.6 3DOD            │        │
│ │ Lead: Alex Lee      │ │ Lead: Chris Wong    │        │
│ │ ────────────────────│ │ ────────────────────│        │
│ │ Progress: 65% 🟡    │ │ Progress: 23% 🔴    │        │
│ │ Hours: 156/240      │ │ Hours: 107/450      │        │
│ │ Tasks: 5/9 ✓        │ │ Tasks: 2/15 ✓       │        │
│ │ Members: 6 active   │ │ Members: 8 (2 low)  │        │
│ │ Status: At Risk     │ │ Status: Blocked     │        │
│ └─────────────────────┘ └─────────────────────┘        │
│ [... 14 more team cards in responsive grid]            │
└─────────────────────────────────────────────────────────┘
```

**Card Metrics**:
- Team WBS number + name
- Team lead name(s)
- Progress % with status indicator (🟢≥75%, 🟡50-74%, 🔴<50%)
- Hours logged / estimated
- Tasks completed / total
- Active members + outlier count
- Status label (On Track / At Risk / Blocked)

**Sorting Options**:
- Progress % (low to high / high to low)
- Hours logged (ascending / descending)
- Team name (alphabetical)
- Status (blocked first, on-track last)

**Interactions**:
- Click card → Team Detail Page
- Hover for quick stats tooltip

---

### PAGE 3: Team Detail Page
**Purpose**: Deep dive into single team's tasks, members, and blockers

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ ◀ Back | 1.6 3DOD (3-Dimensional Object Display)        │
│ Lead: Chris Wong LEAD | Members: 8                      │
├─────────────────────────────────────────────────────────┤
│ Team Summary:                                           │
│ Progress: [23%] ██░░░░░░░░     Status: 🔴 Blocked      │
│ Hours: 106.5 / 450 estimated   Variance: -76.3%        │
│ Tasks: 2 complete, 8 in-progress, 5 not started        │
├─────────────────────────────────────────────────────────┤
│ Subgroups:                                              │
│ ├─ 1.6.1 Interface Design (45% complete)               │
│ ├─ 1.6.2 Hardware Integration (10% complete)           │
│ └─ 1.6.3 Software Development (5% complete)            │
├─────────────────────────────────────────────────────────┤
│ Task List:                                              │
│ ┌─────────────────────────────────────────────────────┐│
│ │Task          │Assignee   │Est │Act │Prog│Status    ││
│ ├─────────────────────────────────────────────────────┤│
│ │PCB Design    │Alice Chen │40  │35  │100%│✓ Complete││
│ │Housing CAD   │Bob Lee    │60  │48  │75% │In Progress││
│ │Code Base     │Chris Wong │80  │0   │0%  │🔴 Blocked││
│ │Testing       │Unassigned │30  │0   │0%  │Not Started││
│ │[... 11 more tasks]                                  ││
│ └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│ Member Contributions (This Week):                       │
│ ┌──────────────────┬────────┬────────┬────────┐        │
│ │ Name             │ Role   │ Hours  │ Status │        │
│ ├──────────────────┼────────┼────────┼────────┤        │
│ │ Chris Wong       │ LEAD   │ 14h    │ 🟢 OK  │        │
│ │ Alice Chen       │ MEM    │ 11h    │ 🟢 OK  │        │
│ │ Bob Lee          │ MEM    │ 10h    │ 🟢 OK  │        │
│ │ David Park       │ MEM    │ 5h     │ 🔴 Low │        │
│ │ Emma Garcia      │ MEM    │ 2h     │ 🔴 Low │        │
│ └──────────────────┴────────┴────────┴────────┘        │
├─────────────────────────────────────────────────────────┤
│ 🚨 Action Items for Lead:                              │
│ • 5 tasks have no estimated hours                      │
│ • Task "Code Base": 0% progress despite being started  │
│ • 2 members below 7h threshold for 2 consecutive weeks │
│ • "Testing" task unassigned, blocking next milestone   │
├─────────────────────────────────────────────────────────┤
│ Recent Updates & Comments:                              │
│ [Feb 6] Chris Wong: "Waiting on parts from supplier"   │
│ [Feb 4] Alice Chen: "PCB design complete, sent to fab" │
└─────────────────────────────────────────────────────────┘
```

**Sections**:
1. **Team Summary**: Progress bar, hours, variance, task counts
2. **Subgroups**: Hierarchical WBS breakdown (1.6.1, 1.6.2, etc.)
3. **Task List**: Sortable table with estimates, actuals, progress, assignees
4. **Member Contributions**: Weekly hours with outlier badges
5. **Action Items**: Auto-generated alerts for lead (missing estimates, zero-progress, low contributors)
6. **Recent Updates**: Latest comments from TeamGantt

**Interactions**:
- Edit task estimates/actuals inline
- Click member name → Member Detail view
- Export team report as PDF

---

### PAGE 4: WBS Hierarchy View
**Purpose**: Full project tree structure with rollup calculations

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ WORK BREAKDOWN STRUCTURE - HIERARCHICAL VIEW            │
│ [Expand All] [Collapse All] [Export Outline]            │
├─────────────────────────────────────────────────────────┤
│ ▼ 1.0 Autoronto SAE 2026 (43% complete) 🟡             │
│   ├─ Est: 2,500h | Act: 1,234h | Var: -50.6%          │
│   │                                                     │
│   ├─▼ 1.1 Project Management (87% complete) 🟢         │
│   │   ├─ Est: 120h | Act: 104h | Var: -13.3%          │
│   │   ├─ 1.1.1 Planning: 100% ✓                       │
│   │   ├─ 1.1.2 Scheduling: 85% (in progress)          │
│   │   └─ 1.1.3 Reporting: 75% (in progress)           │
│   │                                                     │
│   ├─▶ 1.2 Kinematics (92% complete) 🟢                 │
│   │   ├─ Est: 280h | Act: 245h | Var: -12.5%          │
│   │                                                     │
│   ├─▼ 1.6 3DOD (23% complete) 🔴                       │
│   │   ├─ Est: 450h | Act: 107h | Var: -76.2%          │
│   │   ├─▶ 1.6.1 Interface Design (45%)                │
│   │   │   ├─ Est: 180h | Act: 81h                     │
│   │   │   ├─ PCB Design: 100% ✓                       │
│   │   │   ├─ Housing CAD: 75%                         │
│   │   │   └─ Wiring Schematic: 50%                    │
│   │   ├─▶ 1.6.2 Hardware Integration (10%)            │
│   │   │   ├─ Est: 150h | Act: 15h                     │
│   │   └─▶ 1.6.3 Software Development (5%)             │
│   │       ├─ Est: 120h | Act: 11h                     │
│   │                                                     │
│   ├─▶ 1.7 Suspension (85% complete) 🟢                 │
│   ├─▶ 1.8 Brakes (72% complete) 🟡                     │
│   └─▶ [... remaining 10 teams]                         │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Expand/collapse nodes (▶/▼ icons)
- Color-coded status at each level
- Rollup calculations: hours and progress bubble up from leaf tasks
- Variance percentage: (Actual - Estimated) / Estimated
- Export as text outline or CSV for status reports

**Rollup Logic**:
- **Hours**: Sum all child tasks
- **Progress**: Weighted average by estimated hours
  - Formula: Σ(child_progress × child_estimated_hours) / Σ(child_estimated_hours)
- **Status**: Worst child status propagates up (🔴 > 🟡 > 🟢)

---

### PAGE 5: At-Risk Tasks Dashboard
**Purpose**: Identify and prioritize tasks needing intervention

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ AT-RISK TASKS & ALERTS                                  │
│ Filter: [All ▼] | Sort by: [Priority ▼]                │
├─────────────────────────────────────────────────────────┤
│ Summary:                                                │
│ 🔴 Critical: 8 tasks   🟡 Warning: 15 tasks             │
├─────────────────────────────────────────────────────────┤
│ 🔴 CRITICAL ISSUES:                                     │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Task: Code Base (1.6.3)                             ││
│ │ Issue: Hours logged (48h) but 0% progress reported ││
│ │ Assigned: Chris Wong LEAD                           ││
│ │ Deadline: Feb 15 (overdue 8 days)                   ││
│ │ Action: Contact lead for status update              ││
│ └─────────────────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────────────────┐│
│ │ Task: Testing Infrastructure (1.3.5)                ││
│ │ Issue: Unassigned, blocking 3 dependent tasks       ││
│ │ Deadline: Feb 10 (3 days away)                      ││
│ │ Action: Assign to Controls team member              ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ 🟡 WARNINGS:                                            │
│ ┌─────────────────────────────────────────────────────┐│
│ │ Task: Chassis Welding (1.4.2)                       ││
│ │ Issue: 95% over estimated hours (58h / 30h est)     ││
│ │ Assigned: Tom Wilson MEM                            ││
│ │ Status: 75% complete                                ││
│ │ Note: May need scope review                         ││
│ └─────────────────────────────────────────────────────┘│
│ [... 14 more warning items]                            │
└─────────────────────────────────────────────────────────┘
```

**Alert Categories**:
1. **🔴 Critical**:
   - Overdue > 7 days
   - Hours logged but 0% progress
   - Blocking 2+ dependent tasks
   - Unassigned with deadline < 5 days
2. **🟡 Warning**:
   - Overdue 1-7 days
   - Over 150% estimated hours
   - Progress stalled (no updates in 14 days)
   - Missing estimated hours

**Filters**:
- By team
- By alert type
- By assignee
- By deadline (this week, this month, overdue)

---

### PAGE 6: Utilization & Contribution
**Purpose**: Track hour logging trends and identify over/under-contributing members

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ TEAM UTILIZATION & MEMBER CONTRIBUTIONS                 │
│ Week Range: [Jan 13 - Feb 7] | View: [All Teams ▼]     │
├─────────────────────────────────────────────────────────┤
│ Hours Logged Over Time:                                 │
│ [Line Chart: X=weeks, Y=hours]                          │
│  500h ┤                                    ●────        │
│  400h ┤                          ●───●────/             │
│  300h ┤                ●───●────/                       │
│  200h ┤       ●───●───/                                 │
│  100h ┤●────●/                                          │
│     0 └─┬────┬────┬────┬────┬────┬────┬────            │
│       W1  W2  W3  W4  W5  W6  W7  W8                    │
│                                                         │
│ Expected: 680h/week (68 members × 10h avg)              │
│ Actual (this week): 542h (80% of expected)              │
├─────────────────────────────────────────────────────────┤
│ Top 10 Contributors (Last 4 Weeks):                     │
│ ┌──────────────────┬────────┬─────────┬──────────┐     │
│ │ Name             │ Role   │ Hours   │ Avg/Week │     │
│ ├──────────────────┼────────┼─────────┼──────────┤     │
│ │ Alice Chen       │ MEM    │ 58h     │ 14.5h 🟠 │     │
│ │ Chris Wong       │ LEAD   │ 56h     │ 14h      │     │
│ │ Jane Smith       │ LEAD   │ 54h     │ 13.5h    │     │
│ │ Bob Johnson      │ LEAD   │ 53h     │ 13.3h    │     │
│ │ [... 6 more]                                    │     │
│ └──────────────────┴────────┴─────────┴──────────┘     │
├─────────────────────────────────────────────────────────┤
│ 🚨 Outliers This Week:                                  │
│                                                         │
│ 🔴 UNDER-CONTRIBUTING (< 7h threshold):                 │
│ • David Park (MEM): 5h - 2nd consecutive week           │
│ • Emma Garcia (MEM): 2h - 3rd consecutive week          │
│ • [... 10 more members]                                 │
│                                                         │
│ 🟠 OVER-CONTRIBUTING (> 15h threshold):                 │
│ • Alice Chen (MEM): 17h - 2nd consecutive week          │
│ • Tom Wilson (MEM): 16h - 1st week                      │
│ • [... 1 more member]                                   │
├─────────────────────────────────────────────────────────┤
│ Team Efficiency Comparison:                             │
│ [Bar Chart: X=teams, Y=Actual/Est ratio]                │
│ 150% ┤                                      ▓▓          │
│ 100% ┤ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓ ▓▓       ▓▓ ▓▓ ▓▓    ││          │
│  50% ┤                   ▓▓ ▓▓                ▓▓        │
│   0% └────────────────────────────────────────          │
│      1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8 1.9 ...            │
│                                                         │
│ Over-Efficient (>100%): 3DOD (76% under-budget)         │
│ Under-Efficient (<100%): Chassis (195% over-budget)     │
└─────────────────────────────────────────────────────────┘
```

**Metrics**:
- Weekly hours logged trend (line chart)
- Top 10 contributors leaderboard
- Under-contributing members (🔴 < threshold)
- Over-contributing members (🟠 > threshold)
- Team efficiency ratios (actual/estimated)
- Burndown projection to June 2026

**Configuration (PM only)**:
- Low hour threshold: slider 0-10h (default 7h)
- High hour threshold: slider 12-30h (default 15h members, 20h leads)
- Consecutive weeks before alert: 1-4 weeks (default 2)

---

### PAGE 7: Weekly Hour Logging
**Purpose**: Manual entry/review of weekly hours per member

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ WEEKLY HOUR LOGGING - Week of Feb 3-7, 2026            │
│ [◀ Previous Week] [Next Week ▶] [Auto-Distribute]      │
├─────────────────────────────────────────────────────────┤
│ Team: [1.6 3DOD ▼] | Member: [All ▼]                   │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐│
│ │ Member: Chris Wong LEAD (Default: 13h/week)         ││
│ │ ────────────────────────────────────────────────────││
│ │ Task               Mon Tue Wed Thu Fri │ Total  Edit││
│ │ Code Base Setup    2h  2h  1h  1h  0h  │ 6h     [✎] ││
│ │ Architecture Doc   1h  1h  0h  1h  0h  │ 3h     [✎] ││
│ │ Team Meetings      0h  1h  0h  0h  2h  │ 3h     [✎] ││
│ │ Code Review        0h  0h  1h  0h  0h  │ 1h     [✎] ││
│ │ ────────────────────────────────────────────────────││
│ │ Weekly Total: 13h (100% of expected) 🟢             ││
│ │ [Add Task +]                              [Save]    ││
│ └─────────────────────────────────────────────────────┘│
│ ┌─────────────────────────────────────────────────────┐│
│ │ Member: David Park MEM (Default: 10h/week)          ││
│ │ ────────────────────────────────────────────────────││
│ │ Task               Mon Tue Wed Thu Fri │ Total  Edit││
│ │ PCB Testing        2h  1h  0h  0h  0h  │ 3h     [✎] ││
│ │ Documentation      0h  1h  1h  0h  0h  │ 2h     [✎] ││
│ │ ────────────────────────────────────────────────────││
│ │ Weekly Total: 5h (50% of expected) 🔴               ││
│ │ Note: Member flagged for low hours (2nd week)       ││
│ │ [Add Task +]                              [Save]    ││
│ └─────────────────────────────────────────────────────┘│
│ [... more members]                                      │
├─────────────────────────────────────────────────────────┤
│ [Auto-Distribute] will allocate default hours (10h/13h)│
│ across assigned tasks proportionally to estimates      │
│ [Bulk Import CSV] | [Export Week Report]               │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Manual hour entry per task per day
- Auto-distribute button: allocates default hours proportionally
- Visual indicators for under/over-contributing
- CSV import/export for bulk logging
- Save per member or save all

**Auto-Distribution Logic**:
```
For each member with assigned tasks:
  total_allocated = 10h (member) or 13h (lead)
  
  For each assigned task:
    weight = task_estimated_hours / total_estimated_hours_for_member
    task_hours = total_allocated × weight
    
  Distribute across Mon-Fri evenly or based on task dates
```

---

### PAGE 8: Tasks Outstanding
**Purpose**: Comprehensive view of all incomplete work with actionable filtering

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ TASKS OUTSTANDING                                       │
│ Showing: 82 tasks (65 in progress, 17 not started)     │
├─────────────────────────────────────────────────────────┤
│ Filters:                                                │
│ Team: [All ▼] | Status: [In Progress ▼]                │
│ Assignee: [All ▼] | Deadline: [Next 30 days ▼]         │
│ Priority: [All ▼] | Has Issues: [Yes ▼]                │
├─────────────────────────────────────────────────────────┤
│ Sort by: [Deadline ▲] | Group by: [Team ▼]             │
├─────────────────────────────────────────────────────────┤
│ ▼ 1.6 3DOD (13 tasks outstanding)                      │
│ ┌─────────────────────────────────────────────────────┐│
│ │Task             │Assignee  │Est│Act│Prog│Deadline  │Issues ││
│ ├─────────────────────────────────────────────────────┤│
│ │🔴 Code Base     │Wong LEAD │80 │48 │0%  │2/15 ⚠   │0% prog││
│ │🟡 Housing CAD   │Lee MEM   │60 │48 │75% │2/20     │None   ││
│ │⚪ Testing      │Unassigned│30 │0  │0%  │2/10 ⚠⚠ │Unassign││
│ │⚪ Integration   │Chen MEM  │40 │0  │0%  │2/28     │None   ││
│ │[... 9 more tasks]                                   ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ ▼ 1.3 Controls (9 tasks outstanding)                   │
│ ┌─────────────────────────────────────────────────────┐│
│ │🟡 Sensor Calibr │Lee LEAD  │25 │18 │60% │2/14     │None   ││
│ │⚪ Data Logger   │Park MEM  │35 │0  │0%  │3/01     │None   ││
│ │[... 7 more tasks]                                   ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ [... remaining 16 teams]                                │
├─────────────────────────────────────────────────────────┤
│ Quick Actions:                                          │
│ [Export to CSV] [Generate Report] [Bulk Assign]         │
│ [Send Reminder to Leads] [Flag for PM Review]          │
└─────────────────────────────────────────────────────────┘
```

**Task Attributes**:
- **Status Icon**: 🔴 Critical issue, 🟡 Warning, ⚪ Normal
- **Task Name**: Clickable → Task Detail modal
- **Assignee**: Name + role (LEAD/MEM)
- **Est**: Estimated hours
- **Act**: Actual hours logged
- **Prog**: Progress percentage (0%, 25%, 50%, 75%, 100%)
- **Deadline**: Date with urgency indicator (⚠ < 7 days, ⚠⚠ overdue)
- **Issues**: Auto-detected problems (0% progress, unassigned, over-budget)

**Grouping Options**:
- By Team (WBS hierarchy)
- By Deadline (This Week / Next Week / This Month / Later)
- By Assignee (grouped by person)
- By Status (Not Started / In Progress)
- By Priority (Critical / Warning / Normal)

**Filters**:
- **Team**: Dropdown of all 18 teams + "All"
- **Status**: Not Started / In Progress / All
- **Assignee**: All members + "Unassigned" + "All"
- **Deadline**: Custom date range or presets (Next 7/14/30 days, Overdue)
- **Priority**: Critical / Warning / Normal / All
- **Has Issues**: Yes / No / All (filters for tasks with auto-detected problems)

**Quick Actions**:
- **Export to CSV**: Download filtered task list
- **Generate Report**: Create PDF summary for leads/PM
- **Bulk Assign**: Select multiple tasks → assign to member
- **Send Reminder**: Email leads with their outstanding tasks
- **Flag for PM Review**: Mark tasks needing PM intervention

**Task Detail Modal** (on click):
```
┌─────────────────────────────────────────┐
│ Task: Code Base Setup (1.6.3)           │
├─────────────────────────────────────────┤
│ Description: Set up repository and...   │
│ Assigned: Chris Wong LEAD               │
│ Team: 1.6 3DOD                          │
│ Start: Jan 20 | Deadline: Feb 15        │
│ Estimated: 80h | Actual: 48h            │
│ Progress: 0% ⚠                          │
│ Status: 🔴 Critical                     │
├─────────────────────────────────────────┤
│ Issues Detected:                        │
│ • Hours logged but 0% progress reported │
│ • Overdue by 8 days                     │
├─────────────────────────────────────────┤
│ Dependencies:                           │
│ • Blocked by: Architecture Doc ✓        │
│ • Blocking: Testing (1.6.3.2)           │
├─────────────────────────────────────────┤
│ Comments: [View All 3 Comments]         │
│ [Feb 6] "Waiting on parts from supplier"│
├─────────────────────────────────────────┤
│ [Edit Task] [Add Comment] [Close]       │
└─────────────────────────────────────────┘
```

---

## Configuration Settings (PM Access Only)

### Outlier Thresholds
```python
config = {
    # Low hour thresholds
    "low_hour_member": 7,      # hours/week (default 70% of 10h)
    "low_hour_lead": 9,        # hours/week (default 70% of 13h)
    "low_hour_weeks": 2,       # consecutive weeks before alert
    
    # High hour thresholds
    "high_hour_member": 15,    # hours/week (default 150% of 10h)
    "high_hour_lead": 20,      # hours/week (default 150% of 13h)
    "high_hour_weeks": 2,      # consecutive weeks before alert
    
    # Task status thresholds
    "overdue_critical_days": 7,     # days overdue → critical
    "stalled_task_days": 14,        # days no update → warning
    "over_estimate_percent": 150,   # % over estimate → warning
    
    # Team health thresholds
    "on_track_progress": 75,   # % → green status
    "at_risk_progress": 50,    # % → yellow status
    # < 50% → red status
}
```

**Editable via Dashboard**:
- Sliders for hour thresholds
- Dropdown for consecutive week counts
- Number inputs for day/percentage thresholds
- Save/Reset buttons

---

## Technical Architecture

### Technology Stack
**Recommended**: Streamlit (quick prototyping, good for academic presentation)
- **Frontend**: Streamlit widgets (st.columns, st.metric, st.dataframe, st.plotly_chart)
- **Backend**: Python scripts (fetch from TeamGantt API, process data)
- **Data Storage**: Local CSV cache (daily sync) + JSON config file
- **Visualization**: Plotly for interactive charts, st.progress for bars

**Alternative**: Plotly Dash (more polished UI, better for stakeholder demos)

### Data Flow
```
TeamGantt API (source of truth)
    ↓
fetch_teamgantt_data.sh (daily sync via cron)
    ↓
Local CSV/JSON cache (data/*.json, data/*.csv)
    ↓
Dashboard Python scripts (load from cache)
    ↓
Streamlit UI (render pages)
    ↓
User interactions → Update TeamGantt API → Refresh cache
```

### File Structure
```
Autoronto/
├── dashboard/
│   ├── app.py                  # Main Streamlit app entry point
│   ├── config.json             # Outlier thresholds, settings
│   ├── pages/
│   │   ├── 1_executive.py      # Page 1: Executive Dashboard
│   │   ├── 2_team_grid.py      # Page 2: Team Performance Grid
│   │   ├── 3_team_detail.py    # Page 3: Team Detail
│   │   ├── 4_wbs_hierarchy.py  # Page 4: WBS Hierarchy
│   │   ├── 5_at_risk.py        # Page 5: At-Risk Tasks
│   │   ├── 6_utilization.py    # Page 6: Utilization & Contribution
│   │   ├── 7_hour_logging.py   # Page 7: Weekly Hour Logging
│   │   └── 8_tasks_outstanding.py  # Page 8: Tasks Outstanding
│   ├── utils/
│   │   ├── data_loader.py      # Load from CSV/JSON
│   │   ├── calculations.py     # Rollup, variance, progress
│   │   ├── outlier_detection.py # Flag over/under contributors
│   │   └── api_client.py       # TeamGantt API wrapper
│   └── components/
│       ├── team_card.py        # Reusable team card widget
│       ├── task_table.py       # Reusable task table
│       └── charts.py           # Plotly chart templates
├── scripts/
│   ├── log_weekly_hours.py     # Auto-distribute weekly hours
│   ├── suggest_estimates.py    # Populate missing estimates
│   └── sync_data.sh            # Wrapper for daily data sync
└── data/
    ├── config.json             # Dashboard configuration
    └── [cached TeamGantt data]
```

---

## Implementation Priority

### Phase 1: Foundation (Week 1)
1. Set up Streamlit multi-page app structure
2. Implement data loader (read from existing CSV/JSON)
3. Build Page 1 (Executive Dashboard) - basic metrics
4. Build Page 2 (Team Performance Grid) - read-only cards

### Phase 2: Core Features (Week 2)
5. Build Page 3 (Team Detail) with task lists
6. Build Page 4 (WBS Hierarchy) with rollup calculations
7. Build Page 8 (Tasks Outstanding) with filters
8. Implement outlier detection logic

### Phase 3: Advanced Tracking (Week 3)
9. Build Page 6 (Utilization & Contribution) with charts
10. Build Page 7 (Weekly Hour Logging) with manual entry
11. Build Page 5 (At-Risk Tasks) with auto-alerts
12. Add configuration panel for thresholds

### Phase 4: Polish & Testing (Week 4)
13. Add role-based access control
14. Implement data refresh workflow
15. Create auto-distribute hours script
16. User testing and bug fixes
17. Prepare demo for PM presentation

---

## Success Metrics
- ✅ 100% of tasks have estimated hours (currently 0%)
- ✅ 90%+ of members log hours weekly (track adoption)
- ✅ Identify and address 100% of critical at-risk tasks
- ✅ Reduce number of overdue tasks by 50% through visibility
- ✅ Accurate progress tracking: ≤10% variance between reported and actual completion
- ✅ Dashboard used weekly by all 18 team leads for status updates
