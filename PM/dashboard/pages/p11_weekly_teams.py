"""
Page 11: Weekly Team Summary
Team-level view showing actual hours per team per week.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, load_config
from utils.weekly_data_processor import get_available_weeks, get_weekly_team_summary
from components.week_selector import render_week_selector


def render():
    config = load_config()
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    
    st.markdown("""
    <div class="dashboard-header">
        <h1>📅 Weekly Team Summary</h1>
        <p>Team-level hours tracking by week | WBS Resource Utilization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Week selector and sort options
    available_weeks = get_available_weeks(all_tasks, 
                                         config.get("weeks_historical", 8),
                                         config.get("weeks_lookahead", 4))
    
    col_week, col_sort = st.columns([3, 2])
    
    with col_week:
        selected_week = render_week_selector(available_weeks, key="weekly_team_week")
    
    with col_sort:
        sort_by = st.selectbox(
            "Sort By:",
            ["Total Hours ⬇️", "Avg Hours/Member ⬇️", "Team Name ⬆️", "Member Count ⬇️"],
            key="team_sort"
        )
    
    # Get team summary data
    team_summary = get_weekly_team_summary(all_tasks, selected_week, config)
    teams_list = list(team_summary.values())
    
    # Sort teams
    if "Total Hours" in sort_by:
        teams_list = sorted(teams_list, key=lambda x: x["total_hours"], reverse=True)
    elif "Avg Hours" in sort_by:
        teams_list = sorted(teams_list, key=lambda x: x["avg_hours_per_member"], reverse=True)
    elif "Member Count" in sort_by:
        teams_list = sorted(teams_list, key=lambda x: x["member_count"], reverse=True)
    else:  # Team Name
        teams_list = sorted(teams_list, key=lambda x: x["name"])
    
    # Summary metrics
    total_teams = len(teams_list)
    total_hours_all = sum(t["total_hours"] for t in teams_list)
    total_members_all = sum(t["member_count"] for t in teams_list)
    teams_low = len([t for t in teams_list if t["status"] == "low"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_teams}</div>
            <div class="label">Total Teams</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_hours_all:.0f}h</div>
            <div class="label">Total Hours Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_members_all}</div>
            <div class="label">Total Members</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#E74C3C;">{teams_low}</div>
            <div class="label">Underutilized Teams</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Team table
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"#### Team Summary for Selected Week")
    
    if not teams_list:
        st.warning("No team data available for this week.")
    else:
        # Build table
        table_data = []
        for team in teams_list:
            status_emoji = "🔴" if team["status"] == "low" else "🟢"
            table_data.append({
                "Team": team["name"],
                "Members": team["member_count"],
                "Total Hours": f"{team['total_hours']:.1f}h",
                "Avg/Member": f"{team['avg_hours_per_member']:.1f}h",
                "Status": status_emoji
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True, height=min(600, len(df) * 35 + 38))
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export Team Summary",
            data=csv,
            file_name=f"team_summary_{selected_week}.csv",
            mime="text/csv"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Team member breakdown
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Team Member Breakdown")
    
    if teams_list:
        selected_team = st.selectbox(
            "Select a team to view member details:",
            options=["-- Select Team --"] + [t["name"] for t in teams_list],
            key="selected_team_detail"
        )
        
        if selected_team and selected_team != "-- Select Team --":
            team_info = next((t for t in teams_list if t["name"] == selected_team), None)
            
            if team_info:
                st.markdown(f"### {selected_team}")
                
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.metric("Total Hours", f"{team_info['total_hours']:.1f}h")
                with col_t2:
                    st.metric("Members", team_info['member_count'])
                with col_t3:
                    st.metric("Avg/Member", f"{team_info['avg_hours_per_member']:.1f}h")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Member table
                member_data = []
                for member in team_info["members"]:
                    status_badge = {
                        "none": "🔴 None",
                        "low": "🔴 Low",
                        "ok": "🟢 OK",
                        "high": "🟠 High"
                    }[member["status"]]
                    
                    member_data.append({
                        "Name": member["name"],
                        "Role": member["role"],
                        "Tasks": member["task_count"],
                        "Hours": f"{member['hours']:.1f}h",
                        "Status": status_badge
                    })
                
                df_members = pd.DataFrame(member_data)
                st.dataframe(df_members, use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # WBS Integration Note
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-card" style="border:1px solid #2E86AB;">
        <h4 style="color:#2E86AB;">📊 WBS Team Resource Tracking</h4>
        <p style="color:#8899AA; font-size:13px;">
            Per SAE ADCII rules, the WBS must show <b>hrs/wk per person</b> and demonstrate
            resource optimization across teams. This page provides a team-level rollup view,
            making it easy to identify underutilized teams (avg < 7h/member) during the presentation.
            <br><br>
            <b>Presentation tip:</b> Select an underutilized team to drill into member details
            and explain your rebalancing strategy to judges.
        </p>
    </div>
    """, unsafe_allow_html=True)
