"""
Page 5: At-Risk Tasks Dashboard
Identify and prioritize tasks needing intervention.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, load_config
from utils.calculations import detect_task_issues, categorize_alert, days_overdue


def render():
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>⚠️ At-Risk Tasks & Alerts</h1>
        <p>Identify and prioritize tasks needing PM intervention</p>
    </div>
    """, unsafe_allow_html=True)

    # Analyze all tasks
    critical_tasks = []
    warning_tasks = []

    for task in all_tasks:
        if task["percent_complete"] == 100:
            continue
        issues = detect_task_issues(task, config)
        if not issues:
            continue
        category = categorize_alert(issues)
        task_info = {**task, "issues": issues, "category": category}
        if category == "critical":
            critical_tasks.append(task_info)
        else:
            warning_tasks.append(task_info)

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#E74C3C;">{len(critical_tasks)}</div>
            <div class="label">🔴 Critical Issues</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#F39C12;">{len(warning_tasks)}</div>
            <div class="label">🟡 Warnings</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_ok = len([t for t in all_tasks if t["percent_complete"] < 100]) - len(critical_tasks) - len(warning_tasks)
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#2ECC71;">{total_ok}</div>
            <div class="label">⚪ No Issues</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        teams = sorted(set(t["group"] for t in all_tasks))
        filter_team = st.selectbox("Filter by Team", ["All"] + teams)
    with col_f2:
        filter_type = st.selectbox("Filter by Alert Type", ["All", "Critical Only", "Warnings Only"])

    # Critical Issues
    if filter_type in ("All", "Critical Only"):
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🔴 CRITICAL ISSUES")
        filtered_critical = critical_tasks if filter_team == "All" else [t for t in critical_tasks if t["group"] == filter_team]

        if filtered_critical:
            for task in filtered_critical:
                overdue = days_overdue(task.get("end_date"))
                assignees = ", ".join(task["resources"][:3]) or "Unassigned"
                st.markdown(f"""
                <div style="background:#1a0a0a; border:1px solid #E74C3C44; border-radius:8px; padding:12px; margin:8px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:white; font-weight:600;">{task['name']}</span>
                        <span style="color:#8899AA; font-size:12px;">{task['group']}</span>
                    </div>
                    <p style="color:#E74C3C; font-size:13px; margin:4px 0;">{'<br>'.join('• ' + i for i in task['issues'])}</p>
                    <div style="color:#8899AA; font-size:12px;">
                        Assigned: {assignees} | Deadline: {task.get('end_date', '—')} | Progress: {task['percent_complete']}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No critical issues found!")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Warnings
    if filter_type in ("All", "Warnings Only"):
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🟡 WARNINGS")
        filtered_warnings = warning_tasks if filter_team == "All" else [t for t in warning_tasks if t["group"] == filter_team]

        if filtered_warnings:
            rows = []
            for task in filtered_warnings:
                rows.append({
                    "Task": task["name"],
                    "Team": task["group"],
                    "Issues": "; ".join(task["issues"]),
                    "Progress": f"{task['percent_complete']}%",
                    "Act. Hrs": task["actual_hours"],
                    "Deadline": task.get("end_date", "—"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.success("No warnings found!")

        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # UPCOMING TASKS SECTION (NEW)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### 📅 Upcoming Tasks (Proactive Tracking)")
    
    from utils.weekly_data_processor import get_upcoming_tasks
    
    col_weeks = st.columns(4)
    weeks_ahead = []
    for i, label in enumerate(["Next 7 Days", "Week 2", "Week 3", "Week 4"]):
        with col_weeks[i]:
            if st.button(label, key=f"upcoming_{i+1}"):
                weeks_ahead = [i+1]
    
    if not weeks_ahead:
        weeks_ahead = [1, 2, 3, 4]  # Show all by default
    
    upcoming = get_upcoming_tasks(all_tasks, weeks_ahead=max(weeks_ahead))
    
    if upcoming:
        for week_label, tasks in sorted(upcoming.items()):
            with st.expander(f"**{week_label}** — {len(tasks)} tasks due", expanded=True):
                task_data = []
                for task in tasks:
                    days_until = task["days_until_due"]
                    urgency = "🔴" if days_until <= 3 else "🟡" if days_until <= 7 else "🟢"
                    task_data.append({
                        "": urgency,
                        "Task": task["name"],
                        "Team": task["group"],
                        "WBS": task["wbs"],
                        "Due Date": task["end_date"],
                        "Days Until": f"{days_until}d",
                        "Progress": f"{task['progress']}%",
                        "Assigned To": ", ".join(task["assignees"][:2]) or "Unassigned"
                    })
                
                if task_data:
                    df_upcoming = pd.DataFrame(task_data)
                    st.dataframe(df_upcoming, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming tasks in the next 4 weeks.")
    
    st.markdown('</div>', unsafe_allow_html=True)