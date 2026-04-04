"""
Page 1: Executive Dashboard
High-level project health snapshot for PM and stakeholders.
"""
import streamlit as st
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, get_teams, get_project_summary, get_all_resources, load_config
from utils.calculations import get_status_emoji
from components.charts import task_status_pie, team_health_heatmap, progress_gauge, team_progress_bar_chart


def render():
    data = load_hierarchical_data()
    summary = get_project_summary(data)
    teams = get_teams(data)
    config = load_config()

    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1>🏁 aUToronto SAE 2026 — Project Overview</h1>
        <p>R2Y5 Executive Dashboard | Live TeamGantt Integration | Winter Workshop Presentation View</p>
    </div>
    """, unsafe_allow_html=True)

    # Key milestones
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        days_ws = summary["days_to_workshop"]
        color = "#E74C3C" if days_ws <= 7 else "#F39C12" if days_ws <= 14 else "#2ECC71"
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:{color};">{days_ws}</div>
            <div class="label">Days to Winter Workshop (Feb 17)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{summary['days_to_competition']}</div>
            <div class="label">Days to June Competition</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{summary['total_actual_hours']:.0f}h</div>
            <div class="label">Total Hours Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{summary['total_resources']}</div>
            <div class="label">Active Team Members</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress + Task Status
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Project Completion")
        st.plotly_chart(progress_gauge(summary["avg_progress"], "Overall Progress"), use_container_width=True)
        st.markdown(f"""
        <div style="display:flex; justify-content:space-around; text-align:center; margin-top:8px;">
            <div><span style="font-size:20px; font-weight:700; color:#2ECC71;">{summary['completed']}</span><br><span style="color:#8899AA; font-size:11px;">Complete</span></div>
            <div><span style="font-size:20px; font-weight:700; color:#F39C12;">{summary['in_progress']}</span><br><span style="color:#8899AA; font-size:11px;">In Progress</span></div>
            <div><span style="font-size:20px; font-weight:700; color:#8899AA;">{summary['not_started']}</span><br><span style="color:#8899AA; font-size:11px;">Not Started</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Task Status Distribution")
        st.plotly_chart(
            task_status_pie(summary["completed"], summary["in_progress"], summary["not_started"]),
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Critical Alerts
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### 🚨 Critical Alerts")
    
    # Get weekly data for this week
    from utils.weekly_data_processor import get_available_weeks, get_weekly_member_data
    all_tasks = get_all_tasks(data)
    available_weeks = get_available_weeks(all_tasks, config.get("weeks_historical", 8), config.get("weeks_lookahead", 4))
    current_week = next((w["start"] for w in available_weeks if w.get("is_current")), date.today())
    weekly_members = get_weekly_member_data(all_tasks, current_week, config)
    
    inactive_count = len([m for m in weekly_members.values() if m["status"] == "none"])
    overloaded_count = len([m for m in weekly_members.values() if m["status"] == "high"])
    
    alert_col1, alert_col2, alert_col3, alert_col4, alert_col5 = st.columns(5)
    with alert_col1:
        st.metric("Teams Behind Schedule", summary["teams_behind"], delta=None)
    with alert_col2:
        st.metric("Teams At Risk", summary["teams_at_risk"], delta=None)
    with alert_col3:
        st.metric("Overdue Tasks", summary["overdue_tasks"], delta=None)
    with alert_col4:
        color = "#E74C3C" if inactive_count > 10 else "#8899AA"
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:24px; font-weight:700; color:{color};">{inactive_count}</div>
            <div style="font-size:11px; color:#8899AA;">Inactive This Week</div>
        </div>
        """, unsafe_allow_html=True)
    with alert_col5:
        color = "#F39C12" if overloaded_count > 5 else "#8899AA"
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:24px; font-weight:700; color:{color};">{overloaded_count}</div>
            <div style="font-size:11px; color:#8899AA;">Overloaded This Week</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Team Health Heatmap
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Team Health Grid")
    st.markdown("<p style='color:#8899AA; font-size:12px;'>Click any team on the sidebar to view details. Color = progress toward completion.</p>", unsafe_allow_html=True)
    st.plotly_chart(team_health_heatmap(teams), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TeamGantt Integration Banner
    st.markdown("""
    <div class="metric-card" style="border: 1px solid #2E86AB;">
        <div style="display:flex; align-items:center; gap:16px;">
            <div style="font-size:32px;">⚡</div>
            <div>
                <h4 style="margin:0; color:#2E86AB;">TeamGantt Backend Integration</h4>
                <p style="margin:4px 0 0; color:#8899AA; font-size:13px;">
                    This dashboard reads live data from TeamGantt's REST API (Project R2Y5, ID: 4336931).
                    Tasks, WBS structure, resource assignments, and time tracking are all synced from TeamGantt.
                    <br><b>API Endpoints Used:</b> PATCH /tasks/{id} (estimates), POST /times (time blocks), GET /projects/{id}/children (hierarchy)
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
