"""
Page 10: All Members Overview
Consolidated view of EVERY member across all teams with task/hours dual focus.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, load_config
from utils.weekly_data_processor import get_available_weeks, get_weekly_member_data
from components.week_selector import render_week_selector
from components.member_card import render_member_weekly_breakdown


def render():
    config = load_config()
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    
    st.markdown("""
    <div class="dashboard-header">
        <h1>👥 All Members Overview</h1>
        <p>Consolidated view of every member across all teams | Weekly Task & Hours Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Week selector
    available_weeks = get_available_weeks(all_tasks, 
                                         config.get("weeks_historical", 8),
                                         config.get("weeks_lookahead", 4))
    
    col_week, col_view, col_sort, col_filter = st.columns([2, 2, 2, 2])
    
    with col_week:
        selected_week = render_week_selector(available_weeks, key="all_members_week")
    
    with col_view:
        view_mode = st.selectbox(
            "View Mode:",
            ["📋 Task-Focused", "⏱️ Hours-Focused"],
            key="view_mode"
        )
    
    with col_sort:
        sort_order = st.selectbox(
            "Sort Order:",
            ["⬇️ Descending", "⬆️ Ascending"],
            key="sort_order"
        )
    
    with col_filter:
        show_filter = st.selectbox(
            "Show:",
            ["All Members", "Outliers Only", "Active Only", "Inactive Only"],
            key="show_filter"
        )
    
    # Get weekly member data
    member_data = get_weekly_member_data(all_tasks, selected_week, config)
    members_list = list(member_data.values())
    
    # Apply filters
    if show_filter == "Outliers Only":
        members_list = [m for m in members_list if m["status"] in ["none", "low", "high"]]
    elif show_filter == "Active Only":
        members_list = [m for m in members_list if m["hours"] > 0]
    elif show_filter == "Inactive Only":
        members_list = [m for m in members_list if m["hours"] == 0]
    
    # Sort
    sort_key = "task_count" if "Task" in view_mode else "hours"
    ascending = "Ascending" in sort_order
    members_list = sorted(members_list, key=lambda x: x[sort_key], reverse=not ascending)
    
    # Summary metrics
    total_members = len(member_data)
    active_members = len([m for m in member_data.values() if m["hours"] > 0])
    high_activity = len([m for m in member_data.values() if m["status"] == "high"])
    low_activity = len([m for m in member_data.values() if m["status"] in ["low", "none"]])
    total_hours = sum(m["hours"] for m in member_data.values())
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_members}</div>
            <div class="label">Total Members</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{active_members}</div>
            <div class="label">Active This Week</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#E74C3C;">{low_activity}</div>
            <div class="label">Low/Inactive</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value" style="color:#F39C12;">{high_activity}</div>
            <div class="label">High Activity</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_hours:.0f}h</div>
            <div class="label">Total Hours</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Task count filter slider
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    col_slider, col_search = st.columns([3, 2])
    with col_slider:
        if members_list:
            max_tasks = max(m["task_count"] for m in members_list)
            task_range = st.slider(
                "Filter by Task Count:",
                0, max(max_tasks, 1), (0, max(max_tasks, 1)),
                key="task_range"
            )
            members_list = [m for m in members_list if task_range[0] <= m["task_count"] <= task_range[1]]
    
    with col_search:
        search_term = st.text_input("🔍 Search Member:", key="search_member")
        if search_term:
            members_list = [m for m in members_list if search_term.lower() in m["name"].lower()]
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main table
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"#### All Members ({len(members_list)} shown)")
    
    if not members_list:
        st.warning("No members match the current filters.")
    else:
        # Build table data
        table_data = []
        for m in members_list:
            status_badge = {
                "none": "🔴 None",
                "low": "🔴 Low",
                "ok": "🟢 OK",
                "high": "🟠 High"
            }[m["status"]]
            
            table_data.append({
                "Name": m["name"],
                "Team": m["team"],
                "Role": m["role"],
                "Tasks": m["task_count"],
                "Hours": f"{m['hours']:.1f}h",
                "Status": status_badge
            })
        
        df = pd.DataFrame(table_data)
        
        # Display with row selection for details
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=min(600, len(df) * 35 + 38)
        )
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"all_members_{selected_week}.csv",
            mime="text/csv"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Member detail expansion
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Member Detail View")
    
    if members_list:
        selected_member = st.selectbox(
            "Select a member to view their weekly breakdown:",
            options=["-- Select Member --"] + [m["name"] for m in members_list],
            key="selected_member_detail"
        )
        
        if selected_member and selected_member != "-- Select Member --":
            # Get member's weekly history
            from utils.data_loader import get_member_weekly_breakdown
            weekly_history = get_member_weekly_breakdown(selected_member, data, weeks=config.get("weeks_historical", 8))
            
            # Find selected member's data for this week
            member_info = next((m for m in members_list if m["name"] == selected_member), None)
            
            if member_info:
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                with col_info1:
                    st.metric("Team", member_info["team"])
                with col_info2:
                    st.metric("Role", member_info["role"])
                with col_info3:
                    st.metric("This Week Tasks", member_info["task_count"])
                with col_info4:
                    st.metric("This Week Hours", f"{member_info['hours']:.1f}h")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Show tasks for this week
                if member_info["task_list"]:
                    st.markdown("**Tasks This Week:**")
                    for i, task in enumerate(member_info["task_list"][:15], 1):
                        st.markdown(f"{i}. {task}")
                    if len(member_info["task_list"]) > 15:
                        st.markdown(f"*... and {len(member_info['task_list']) - 15} more*")
            
            st.markdown("<br>", unsafe_allow_html=True)
            render_member_weekly_breakdown(selected_member, weekly_history)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # WBS Integration Note
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-card" style="border:1px solid #2E86AB;">
        <h4 style="color:#2E86AB;">💡 WBS Presentation Tip</h4>
        <p style="color:#8899AA; font-size:13px;">
            <b>For SAE judges:</b> This page demonstrates your team's WBS proficiency by showing
            <b>individual member workloads week-by-week</b>. Use the dual-focus views (Task vs Hours)
            to identify overloaded members and rebalance workload — a key WBS evaluation criterion.
            <br><br>
            <b>During presentation:</b> Toggle between Task-Focused and Hours-Focused views to show
            how you monitor both dimensions. Click a member to display their weekly breakdown as evidence
            of ongoing WBS utilization.
        </p>
    </div>
    """, unsafe_allow_html=True)
