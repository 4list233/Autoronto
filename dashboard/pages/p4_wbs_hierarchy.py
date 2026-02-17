"""
Page 4: WBS Hierarchy View
Full project tree structure with rollup calculations.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, load_config
from utils.calculations import get_status_emoji, calculate_weighted_progress


def render():
    data = load_hierarchical_data()
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>🌳 Work Breakdown Structure — Hierarchical View</h1>
        <p>Full project tree with rollup calculations | SAE AutoDrive WBS Requirement</p>
    </div>
    """, unsafe_allow_html=True)

    # WBS explanation banner
    st.markdown("""
    <div class="metric-card" style="border:1px solid #2E86AB; margin-bottom:16px;">
        <h4 style="color:#2E86AB; margin:0;">WBS + TeamGantt Integration</h4>
        <p style="color:#8899AA; font-size:13px; margin:4px 0 0;">
            This view maps directly from TeamGantt's hierarchical project structure.
            Each group represents a team/subteam, with tasks nested underneath.
            <b>Rollup logic:</b> Progress = average of task completion %; Status = worst child propagates up.
            <br><b>hrs/wk per person</b> tracked via TeamGantt time blocks (POST /v1/times).
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        expand_all = st.checkbox("Expand All", value=True)

    # Build tree
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    def render_node(item, depth=0):
        indent = "&nbsp;" * (depth * 6)
        prefix_icon = "├─"

        if item.get("type") in ("group", "subgroup"):
            children = item.get("children", [])
            tasks_in_group = get_tasks_recursive(children)
            total_act = sum(t.get("actual_hours", 0) for t in tasks_in_group)

            if tasks_in_group:
                avg_progress = sum(t.get("percent_complete", 0) for t in tasks_in_group) / len(tasks_in_group)
            else:
                avg_progress = 0

            emoji = get_status_emoji(avg_progress, config["on_track_progress"], config["at_risk_progress"])
            name = item.get("name", "Unknown")

            # Top-level groups get gold, subgroups get lighter color
            color = "#F6AE2D" if item.get("type") == "group" else "#2E86AB"
            st.markdown(f"""
            {indent} <span style="color:{color}; font-weight:600;">▼ {name}</span>
            <span style="color:#8899AA;">({avg_progress:.0f}% complete) {emoji}</span>
            <br>{indent}&nbsp;&nbsp;&nbsp;
            <span style="color:#556677; font-size:12px;">Actual: {total_act:.1f}h | Tasks: {len(tasks_in_group)}</span>
            """, unsafe_allow_html=True)

            if expand_all:
                for child in children:
                    render_node(child, depth + 1)

        elif item.get("type") in ("task", "milestone"):
            pct = item.get("percent_complete", 0)
            act = item.get("actual_hours", 0)
            wbs = item.get("wbs", "")
            name = item.get("name", "")

            if pct == 100:
                icon = "✅"
            elif pct > 0:
                icon = "🔧"
            else:
                icon = "⬜"

            resources = [r.get("name", "") if isinstance(r, dict) else r for r in item.get("resources", [])]
            res_str = ", ".join(resources[:2]) if resources else "Unassigned"

            type_badge = "🔷" if item.get("type") == "milestone" else ""

            st.markdown(f"""
            {indent} {prefix_icon} {icon} {type_badge} <span style="color:white;">{wbs} {name}</span>
            <span style="color:#8899AA; font-size:12px;"> — {pct}% | {act:.1f}h logged | {res_str}</span>
            """, unsafe_allow_html=True)

    def get_tasks_recursive(items):
        tasks = []
        for item in items:
            if item.get("type") in ("task", "milestone"):
                tasks.append(item)
            if "children" in item:
                tasks.extend(get_tasks_recursive(item["children"]))
        return tasks

    # Render the full tree
    project_name = config.get("project_name", "R2Y5")
    all_tasks = get_tasks_recursive(data)
    total_act = sum(t.get("actual_hours", 0) for t in all_tasks)
    overall_progress = sum(t.get("percent_complete", 0) for t in all_tasks) / max(len(all_tasks), 1)
    emoji = get_status_emoji(overall_progress, config["on_track_progress"], config["at_risk_progress"])

    st.markdown(f"""
    <h3 style="color:#F6AE2D;">▼ 1.0 {project_name} ({overall_progress:.0f}% complete) {emoji}</h3>
    <span style="color:#8899AA;">Actual: {total_act:.1f}h | Teams: {len(data)} | Tasks: {len(all_tasks)}</span>
    """, unsafe_allow_html=True)
    st.divider()

    for group in data:
        render_node(group, depth=1)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Rollup logic explanation
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-card" style="border:1px solid #556677;">
        <h4 style="color:#8899AA;">Rollup Calculation Logic</h4>
        <ul style="color:#8899AA; font-size:13px;">
            <li><b>Hours:</b> Sum of actual hours from all child tasks</li>
            <li><b>Progress:</b> Average of child task completion percentages. Formula: Σ(child_percent_complete) / num_children</li>
            <li><b>Status:</b> Worst child status propagates up (🔴 > 🟡 > 🟢)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
