"""
Page 2: Team Performance Grid
Compare all 18 teams side-by-side, identify lagging teams.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_teams, load_config
from components.team_card import render_team_card
from components.charts import team_progress_bar_chart, hours_comparison_chart


def render():
    data = load_hierarchical_data()
    teams = get_teams(data)
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>📊 Team Performance Overview</h1>
        <p>Compare all teams side-by-side | Sort and filter to identify lagging teams</p>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox("Sort by", ["Progress (Low→High)", "Progress (High→Low)", "Hours Logged", "Team Name", "Status (Behind First)"])
    with col2:
        filter_status = st.selectbox("Filter Status", ["All", "On Track", "At Risk", "Behind"])
    with col3:
        view_mode = st.radio("View", ["Cards", "Chart"], horizontal=True)

    # Sort
    if sort_by == "Progress (Low→High)":
        teams.sort(key=lambda t: t["progress"])
    elif sort_by == "Progress (High→Low)":
        teams.sort(key=lambda t: t["progress"], reverse=True)
    elif sort_by == "Hours Logged":
        teams.sort(key=lambda t: t["actual_hours"], reverse=True)
    elif sort_by == "Team Name":
        teams.sort(key=lambda t: t["name"])
    elif sort_by == "Status (Behind First)":
        status_order = {"Behind": 0, "At Risk": 1, "On Track": 2}
        teams.sort(key=lambda t: status_order.get(t["status"], 3))

    # Filter
    if filter_status != "All":
        teams = [t for t in teams if t["status"] == filter_status]

    if view_mode == "Chart":
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Team Progress Comparison")
        st.plotly_chart(team_progress_bar_chart(teams), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### Hours: Estimated vs Actual")
        st.plotly_chart(hours_comparison_chart(teams), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Card grid: 3 columns
        cols = st.columns(3)
        for i, team in enumerate(teams):
            with cols[i % 3]:
                render_team_card(team)

    # Summary stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Summary Statistics")
    scol1, scol2, scol3, scol4 = st.columns(4)
    with scol1:
        on_track = len([t for t in teams if t["status"] == "On Track"])
        st.metric("🟢 On Track", on_track)
    with scol2:
        at_risk = len([t for t in teams if t["status"] == "At Risk"])
        st.metric("🟡 At Risk", at_risk)
    with scol3:
        behind = len([t for t in teams if t["status"] == "Behind"])
        st.metric("🔴 Behind", behind)
    with scol4:
        total_hours = sum(t["actual_hours"] for t in teams)
        st.metric("Total Hours", f"{total_hours:.0f}h")
    st.markdown('</div>', unsafe_allow_html=True)
