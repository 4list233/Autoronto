"""
Page 3: Team Detail Page
Deep dive into single team's tasks, members, and blockers.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, get_teams, load_config
from utils.calculations import get_status_emoji, detect_task_issues, days_overdue
from components.charts import progress_gauge


def render():
    data = load_hierarchical_data()
    teams = get_teams(data)
    all_tasks = get_all_tasks(data)
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>👥 Team Detail View</h1>
        <p>Deep dive into individual team tasks, members, and action items</p>
    </div>
    """, unsafe_allow_html=True)

    # Team selector
    team_names = [t["name"] for t in teams]
    selected_name = st.selectbox("Select Team", team_names)
    team = next((t for t in teams if t["name"] == selected_name), None)

    if not team:
        st.warning("No team selected.")
        return

    team_tasks = [t for t in all_tasks if t["group"] == selected_name]

    # Team summary header
    emoji = get_status_emoji(team["progress"])
    col1, col2 = st.columns([1, 2])
    with col1:
        st.plotly_chart(progress_gauge(team["progress"], selected_name), use_container_width=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color:#F6AE2D; margin:0;">{emoji} {selected_name}</h3>
            <p style="color:#8899AA;">Lead(s): {', '.join(team['leads']) or 'Unassigned'}</p>
            <div style="display:flex; gap:24px; margin-top:12px;">
                <div>
                    <span style="font-size:24px; font-weight:700; color:white;">{team['actual_hours']:.0f}h</span>
                    <br><span style="color:#8899AA; font-size:11px;">Hours Logged</span>
                </div>
                <div>
                    <span style="font-size:24px; font-weight:700; color:white;">{team['completed']}/{team['total_tasks']}</span>
                    <br><span style="color:#8899AA; font-size:11px;">Tasks Complete</span>
                </div>
                <div>
                    <span style="font-size:24px; font-weight:700; color:white;">{team['member_count']}</span>
                    <br><span style="color:#8899AA; font-size:11px;">Members</span>
                </div>
                <div>
                    <span style="font-size:24px; font-weight:700; color:{'#2ECC71' if team['status']=='On Track' else '#F39C12' if team['status']=='At Risk' else '#E74C3C'};">{team['status']}</span>
                    <br><span style="color:#8899AA; font-size:11px;">Status</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Task list
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Task List")

    if team_tasks:
        rows = []
        for t in team_tasks:
            issues = detect_task_issues(t, config)
            overdue = days_overdue(t.get("end_date"))
            if issues and any("CRITICAL" in i for i in issues):
                icon = "🔴"
            elif issues:
                icon = "🟡"
            elif t["percent_complete"] == 100:
                icon = "✅"
            else:
                icon = "⚪"

            rows.append({
                "": icon,
                "Task": t["name"],
                "Type": t["type"],
                "Assignees": ", ".join(t["resources"][:3]),
                "Est. Hrs": t["estimated_hours"],
                "Act. Hrs": t["actual_hours"],
                "Progress": f"{t['percent_complete']}%",
                "Deadline": t.get("end_date", "—"),
                "Issues": "; ".join(issues) if issues else "—",
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True, height=min(500, len(rows) * 38 + 38))
    else:
        st.info("No tasks found for this team.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Member contributions
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Member Contributions")

    resource_hours = {}
    for t in team_tasks:
        n_res = max(len(t["resources"]), 1)
        for r in t["resources"]:
            if r not in resource_hours:
                resource_hours[r] = {"name": r, "hours": 0, "tasks": 0}
            resource_hours[r]["hours"] += t["actual_hours"] / n_res
            resource_hours[r]["tasks"] += 1

    if resource_hours:
        mem_rows = []
        for r in sorted(resource_hours.values(), key=lambda x: -x["hours"]):
            is_lead = "LEAD" in r["name"].upper()
            role = "LEAD" if is_lead else "MEM"
            threshold = config["low_hour_lead"] if is_lead else config["low_hour_member"]
            high_threshold = config["high_hour_lead"] if is_lead else config["high_hour_member"]

            if r["hours"] < threshold:
                status = "🔴 Low"
            elif r["hours"] > high_threshold:
                status = "🟠 High"
            else:
                status = "🟢 OK"

            mem_rows.append({
                "Name": r["name"],
                "Role": role,
                "Hours": f"{r['hours']:.1f}h",
                "Tasks": r["tasks"],
                "Status": status,
            })

        df_mem = pd.DataFrame(mem_rows)
        st.dataframe(df_mem, use_container_width=True, hide_index=True)
    else:
        st.info("No member data available.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action Items
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### 🚨 Action Items for Lead")
    action_items = []

    zero_est = [t for t in team_tasks if t["estimated_hours"] == 0]
    if zero_est:
        action_items.append(f"**{len(zero_est)} tasks** have no estimated hours")

    zero_prog = [t for t in team_tasks if t["actual_hours"] > 0 and t["percent_complete"] == 0]
    if zero_prog:
        for t in zero_prog:
            action_items.append(f'Task "{t["name"]}": {t["actual_hours"]}h logged but 0% progress reported')

    unassigned = [t for t in team_tasks if not t["resources"]]
    if unassigned:
        for t in unassigned:
            action_items.append(f'Task "{t["name"]}" is unassigned')

    overdue_list = [t for t in team_tasks if days_overdue(t.get("end_date")) > 0 and t["percent_complete"] < 100]
    if overdue_list:
        for t in overdue_list:
            action_items.append(f'Task "{t["name"]}" is overdue by {days_overdue(t["end_date"])} days')

    if action_items:
        for item in action_items:
            st.markdown(f"- {item}")
    else:
        st.success("No critical action items for this team.")

    st.markdown('</div>', unsafe_allow_html=True)
