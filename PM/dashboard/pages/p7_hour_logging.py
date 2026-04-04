"""
Page 7: Weekly Hour Logging
Manual entry/review of weekly hours per member.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, get_teams, load_config


def render():
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    teams = get_teams(data)
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>⏱️ Weekly Hour Logging</h1>
        <p>Review and manage weekly hours per member per task | Auto-distribute available</p>
    </div>
    """, unsafe_allow_html=True)

    # Week selector
    today = date.today()
    # Find Monday of current week
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ Previous Week"):
            if "week_offset" not in st.session_state:
                st.session_state.week_offset = 0
            st.session_state.week_offset -= 1
    with col3:
        if st.button("Next Week ▶"):
            if "week_offset" not in st.session_state:
                st.session_state.week_offset = 0
            st.session_state.week_offset += 1

    offset = st.session_state.get("week_offset", 0)
    week_monday = monday + timedelta(weeks=offset)
    week_friday = week_monday + timedelta(days=4)

    with col2:
        st.markdown(f"<h3 style='text-align:center; color:#F6AE2D;'>Week of {week_monday.strftime('%b %d')} - {week_friday.strftime('%b %d, %Y')}</h3>", unsafe_allow_html=True)

    # Team and member selectors
    col_t, col_m = st.columns(2)
    with col_t:
        team_names = ["All"] + [t["name"] for t in teams]
        selected_team = st.selectbox("Team", team_names)
    with col_m:
        if selected_team == "All":
            team_tasks = all_tasks
        else:
            team_tasks = [t for t in all_tasks if t["group"] == selected_team]

        all_members = set()
        for t in team_tasks:
            all_members.update(t.get("resources", []))
        member_list = ["All"] + sorted(all_members)
        selected_member = st.selectbox("Member", member_list)

    st.markdown("<br>", unsafe_allow_html=True)

    # Auto-distribute explanation
    st.markdown("""
    <div class="metric-card" style="border:1px solid #F6AE2D44;">
        <div style="display:flex; gap:12px; align-items:center;">
            <span style="font-size:24px;">⚡</span>
            <div>
                <p style="color:#F6AE2D; font-weight:600; margin:0;">Auto-Distribution Logic</p>
                <p style="color:#8899AA; font-size:12px; margin:2px 0 0;">
                    Allocates hours across assigned tasks based on actual tracked time.
                    Uses TeamGantt's POST /v1/times endpoint to create time blocks.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display member hour logging cards
    if selected_member != "All":
        members_to_show = [selected_member]
    elif selected_team != "All":
        members_to_show = sorted(all_members)
    else:
        members_to_show = sorted(all_members)[:10]  # Limit to first 10

    for member in members_to_show:
        member_tasks = [t for t in team_tasks if member in t.get("resources", [])]
        if not member_tasks:
            continue

        is_lead = "LEAD" in member.upper()
        role = "LEAD" if is_lead else "MEM"

        total_logged = sum(t["actual_hours"] / max(len(t["resources"]), 1) for t in member_tasks)
        
        # Determine status based on absolute thresholds
        threshold_low = config.get("low_hour_lead", 9) if is_lead else config.get("low_hour_member", 7)
        threshold_high = config.get("high_hour_lead", 20) if is_lead else config.get("high_hour_member", 15)
        
        if total_logged == 0:
            status_badge = '<span class="badge-red">🔴 None</span>'
        elif total_logged < threshold_low:
            status_badge = '<span class="badge-red">🔴 Low</span>'
        elif total_logged > threshold_high:
            status_badge = '<span class="badge-yellow">🟠 High</span>'
        else:
            status_badge = '<span class="badge-green">🟢 OK</span>'

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:white; font-weight:600; font-size:15px;">{member}</span>
                    <span style="color:#8899AA; font-size:12px;"> {role}</span>
                </div>
                <div>
                    <span style="color:white; font-weight:700; font-size:18px;">{total_logged:.1f}h</span>
                    {status_badge}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Task breakdown
        rows = []
        for t in member_tasks:
            share = t["actual_hours"] / max(len(t["resources"]), 1)
            rows.append({
                "Task": t["name"],
                "Team": t["group"],
                "My Hours": f"{share:.1f}h",
                "Progress": f"{t['percent_complete']}%",
            })

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=min(200, len(rows) * 38 + 38))

        st.markdown("<br>", unsafe_allow_html=True)
