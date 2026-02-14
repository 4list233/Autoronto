"""
Member card component for displaying member details and task breakdown.
"""
import streamlit as st
import pandas as pd


def render_member_card(member_data, show_tasks=True):
    """
    Render an expandable card for a member.
    
    Args:
        member_data: Dict with member info (name, team, role, hours, task_count, task_list, status)
        show_tasks: Whether to show expandable task list
    """
    # Status badge
    status_badges = {
        "none": "🔴 None",
        "low": "🔴 Low",
        "ok": "🟢 OK",
        "high": "🟠 High"
    }
    badge = status_badges.get(member_data.get("status", "ok"), "🟢 OK")
    
    # Main card
    with st.expander(f"**{member_data['name']}** ({member_data['team']}) - {badge}", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Role", member_data.get("role", "MEM"))
        with col2:
            st.metric("Hours", f"{member_data.get('hours', 0):.1f}h")
        with col3:
            st.metric("Tasks", member_data.get("task_count", 0))
        with col4:
            st.metric("Status", badge)
        
        if show_tasks and member_data.get("task_list"):
            st.markdown("#### Tasks")
            tasks = member_data["task_list"]
            if len(tasks) > 0:
                # Display as a simple list
                for i, task in enumerate(tasks[:10]):  # Limit to 10 for display
                    st.markdown(f"- {task}")
                if len(tasks) > 10:
                    st.markdown(f"*... and {len(tasks) - 10} more tasks*")
            else:
                st.info("No tasks assigned this week")


def render_member_weekly_breakdown(member_name, weekly_history):
    """
    Render a member's weekly hours breakdown.
    
    Args:
        member_name: Member name
        weekly_history: List of dicts with week, hours, tasks
    """
    st.markdown(f"#### Weekly Breakdown: {member_name}")
    
    if not weekly_history:
        st.info("No historical data available")
        return
    
    df = pd.DataFrame(weekly_history)
    
    # Create a bar chart
    import plotly.graph_objects as go
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["week"],
        y=df["hours"],
        name="Hours",
        text=df["hours"].round(1),
        textposition="auto",
        marker_color="#2E86AB"
    ))
    
    fig.update_layout(
        title=f"Hours per Week",
        xaxis_title="Week",
        yaxis_title="Hours",
        height=300,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CCDDEE")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show table
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_member_comparison_table(members_data, sort_by="hours", ascending=False):
    """
    Render a sortable table of members.
    
    Args:
        members_data: List of member dicts
        sort_by: Column to sort by ("hours", "task_count", "name")
        ascending: Sort order
    
    Returns:
        DataFrame for further processing
    """
    if not members_data:
        st.warning("No member data available")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df_data = []
    for m in members_data:
        status_emoji = {
            "none": "🔴",
            "low": "🔴",
            "ok": "🟢",
            "high": "🟠"
        }.get(m.get("status", "ok"), "🟢")
        
        df_data.append({
            "Name": m["name"],
            "Team": m.get("team", ""),
            "Role": m.get("role", "MEM"),
            "Tasks": m.get("task_count", 0),
            "Hours": f"{m.get('hours', 0):.1f}h",
            "Status": status_emoji
        })
    
    df = pd.DataFrame(df_data)
    
    # Sort
    sort_col_map = {
        "hours": "Hours",
        "task_count": "Tasks",
        "name": "Name"
    }
    if sort_by in sort_col_map:
        col = sort_col_map[sort_by]
        if col in ["Hours", "Tasks"]:
            # Convert to numeric for sorting
            if col == "Hours":
                df["_sort"] = df["Hours"].str.replace("h", "").astype(float)
            else:
                df["_sort"] = df["Tasks"]
            df = df.sort_values("_sort", ascending=ascending)
            df = df.drop(columns=["_sort"])
        else:
            df = df.sort_values(col, ascending=ascending)
    
    return df
