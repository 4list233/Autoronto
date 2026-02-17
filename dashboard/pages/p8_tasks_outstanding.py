"""
Page 8: Tasks Outstanding
Comprehensive view of all incomplete work with actionable filtering.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, get_teams, load_config
from utils.calculations import detect_task_issues, categorize_alert, days_overdue


def render():
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    teams = get_teams(data)
    config = load_config()

    # Only incomplete tasks
    outstanding = [t for t in all_tasks if t["percent_complete"] < 100]
    in_progress = [t for t in outstanding if t["percent_complete"] > 0]
    not_started = [t for t in outstanding if t["percent_complete"] == 0]

    st.markdown("""
    <div class="dashboard-header">
        <h1>📋 Tasks Outstanding</h1>
        <p>All incomplete work with actionable filtering and quick actions</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    st.markdown(f"""
    <div class="metric-card">
        <span style="color:white; font-size:16px;">
            Showing: <b>{len(outstanding)}</b> tasks
            (<span style="color:#F39C12;">{len(in_progress)} in progress</span>,
             <span style="color:#8899AA;">{len(not_started)} not started</span>)
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        team_names = ["All"] + sorted(set(t["group"] for t in outstanding))
        filter_team = st.selectbox("Team", team_names, key="outstanding_team")
    with col2:
        filter_status = st.selectbox("Status", ["All", "In Progress", "Not Started"])
    with col3:
        filter_issues = st.selectbox("Has Issues", ["All", "Yes", "No"])
    with col4:
        # NEW: Member filter
        all_resources = set()
        for t in outstanding:
            all_resources.update(t.get("resources", []))
        resource_names = ["All"] + sorted(all_resources)
        filter_member = st.selectbox("Member", resource_names, key="outstanding_member")

    col5, col6 = st.columns(2)
    with col5:
        sort_by = st.selectbox("Sort by", ["Deadline", "Progress", "Team", "Hours Logged"])
    with col6:
        group_by = st.selectbox("Group by", ["Team", "Status", "None"])

    # Apply filters
    filtered = outstanding
    if filter_team != "All":
        filtered = [t for t in filtered if t["group"] == filter_team]
    if filter_status == "In Progress":
        filtered = [t for t in filtered if t["percent_complete"] > 0]
    elif filter_status == "Not Started":
        filtered = [t for t in filtered if t["percent_complete"] == 0]
    
    # NEW: Filter by member
    if filter_member != "All":
        filtered = [t for t in filtered if filter_member in t.get("resources", [])]

    # Check issues
    for t in filtered:
        t["_issues"] = detect_task_issues(t, config)
        t["_category"] = categorize_alert(t["_issues"])

    if filter_issues == "Yes":
        filtered = [t for t in filtered if t["_issues"]]
    elif filter_issues == "No":
        filtered = [t for t in filtered if not t["_issues"]]

    # Sort
    if sort_by == "Deadline":
        filtered.sort(key=lambda t: t.get("end_date") or "9999-99-99")
    elif sort_by == "Progress":
        filtered.sort(key=lambda t: t["percent_complete"])
    elif sort_by == "Team":
        filtered.sort(key=lambda t: t["group"])
    elif sort_by == "Hours Logged":
        filtered.sort(key=lambda t: t["actual_hours"], reverse=True)

    # Render grouped
    if group_by == "Team":
        groups = {}
        for t in filtered:
            g = t["group"]
            if g not in groups:
                groups[g] = []
            groups[g].append(t)

        for gname, tasks in sorted(groups.items()):
            st.markdown(f'<div class="metric-card" style="margin-bottom:12px;">', unsafe_allow_html=True)
            st.markdown(f"##### ▼ {gname} ({len(tasks)} tasks outstanding)")
            _render_task_df(tasks)
            st.markdown('</div>', unsafe_allow_html=True)

    elif group_by == "Status":
        if in_prog_filtered := [t for t in filtered if t["percent_complete"] > 0]:
            st.markdown('<div class="metric-card" style="margin-bottom:12px;">', unsafe_allow_html=True)
            st.markdown(f"##### 🔧 In Progress ({len(in_prog_filtered)} tasks)")
            _render_task_df(in_prog_filtered)
            st.markdown('</div>', unsafe_allow_html=True)

        if not_started_filtered := [t for t in filtered if t["percent_complete"] == 0]:
            st.markdown('<div class="metric-card" style="margin-bottom:12px;">', unsafe_allow_html=True)
            st.markdown(f"##### ⬜ Not Started ({len(not_started_filtered)} tasks)")
            _render_task_df(not_started_filtered)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        _render_task_df(filtered)
        st.markdown('</div>', unsafe_allow_html=True)

    # Quick actions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Quick Actions")
    
    # NEW: Show selected member's weekly breakdown
    if filter_member != "All":
        st.markdown(f"##### Weekly Hours for {filter_member}")
        from utils.data_loader import get_member_weekly_breakdown
        weekly_history = get_member_weekly_breakdown(filter_member, data, weeks=config.get("weeks_historical", 8))
        
        if weekly_history:
            import plotly.graph_objects as go
            df_history = pd.DataFrame(weekly_history)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_history["week"],
                y=df_history["hours"],
                name="Hours",
                text=df_history["hours"].round(1),
                textposition="auto",
                marker_color="#2E86AB"
            ))
            
            fig.update_layout(
                xaxis_title="Week",
                yaxis_title="Hours",
                height=250,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CCDDEE"),
                margin=dict(l=40, r=40, t=20, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    qcol1, qcol2, qcol3 = st.columns(3)
    with qcol1:
        if st.button("📥 Export to CSV"):
            _export_csv(filtered)
    with qcol2:
        st.button("📧 Send Reminder to Leads", disabled=True, help="Coming soon: Sends email to team leads with their outstanding tasks")
    with qcol3:
        st.button("🚩 Flag for PM Review", disabled=True, help="Coming soon: Marks selected tasks for PM attention")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_task_df(tasks):
    rows = []
    for t in tasks:
        overdue = days_overdue(t.get("end_date"))
        deadline_str = t.get("end_date", "—")
        if overdue > 7:
            deadline_str += " ⚠️⚠️"
        elif overdue > 0:
            deadline_str += " ⚠️"

        if t.get("_category") == "critical":
            icon = "🔴"
        elif t.get("_category") == "warning":
            icon = "🟡"
        else:
            icon = "⚪"

        rows.append({
            "": icon,
            "Task": t["name"],
            "Team": t["group"],
            "Assignees": ", ".join(t.get("resources", [])[:2]) or "Unassigned",
            "Act. Hrs": t["actual_hours"],
            "Progress": f"{t['percent_complete']}%",
            "Deadline": deadline_str,
            "Issues": "; ".join(t.get("_issues", [])) or "—",
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(400, len(rows) * 38 + 38))


def _export_csv(tasks):
    rows = []
    for t in tasks:
        rows.append({
            "Task": t["name"],
            "Team": t["group"],
            "WBS": t.get("wbs", ""),
            "Assignees": ", ".join(t.get("resources", [])),
            "Actual Hours": t["actual_hours"],
            "Progress": t["percent_complete"],
            "Deadline": t.get("end_date", ""),
            "Issues": "; ".join(t.get("_issues", [])),
        })
    df = pd.DataFrame(rows)
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "tasks_outstanding.csv", "text/csv")
