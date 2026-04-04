"""
Page 4: WBS Hierarchy View
Full project tree structure with rollup calculations.
Merges hierarchical structure with flat data for complete task details.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, load_flat_data, load_config
from utils.calculations import get_status_emoji, calculate_weighted_progress


def _build_flat_lookup(flat_data):
    """Build a lookup dict from flat data keyed by task id."""
    lookup = {}
    for item in flat_data:
        tid = item.get("id")
        if tid:
            lookup[tid] = item
    return lookup


def _enrich_tree(nodes, flat_lookup):
    """Walk the hierarchical tree and merge in fields from flat data."""
    for node in nodes:
        tid = node.get("id")
        flat = flat_lookup.get(tid, {})

        # Merge missing fields from flat data
        if "actual_hours" not in node or node.get("actual_hours") is None:
            node["actual_hours"] = flat.get("actual_hours") or 0
        if "estimated_hours" not in node or node.get("estimated_hours") is None:
            node["estimated_hours"] = flat.get("estimated_hours") or 0
        if "start_date" not in node or node.get("start_date") is None:
            node["start_date"] = flat.get("start_date")
        if "end_date" not in node or node.get("end_date") is None:
            node["end_date"] = flat.get("end_date")
        if "wbs" not in node or node.get("wbs") is None:
            node["wbs"] = flat.get("wbs", "")
        if "dependencies" not in node:
            node["dependencies"] = flat.get("dependencies", [])
        if "has_tracked_time" not in node:
            node["has_tracked_time"] = flat.get("has_tracked_time", False)

        # Normalize resources: hierarchical uses "users", flat uses "resources"
        if "resources" not in node or not node.get("resources"):
            users = node.get("users", [])
            flat_resources = flat.get("resources", [])
            node["resources"] = flat_resources if flat_resources else users

        # Recurse into children
        if "children" in node:
            _enrich_tree(node["children"], flat_lookup)


def render():
    data = load_hierarchical_data()
    flat_data = load_flat_data()
    config = load_config()

    # Enrich hierarchical tree with flat data fields
    flat_lookup = _build_flat_lookup(flat_data)
    _enrich_tree(data, flat_lookup)

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
            <br>Click any task to expand full details.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        expand_all = st.checkbox("Expand All", value=True)
    with col3:
        show_completed = st.checkbox("Show Completed", value=True)

    # Build tree
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    def get_resource_names(item):
        """Extract resource names from either 'resources' or 'users' field."""
        resources = item.get("resources", []) or item.get("users", [])
        names = []
        for r in resources:
            if isinstance(r, dict):
                names.append(r.get("name", ""))
            elif isinstance(r, str):
                names.append(r)
        return names

    def render_task_detail(item):
        """Render a clickable expander with full task details."""
        pct = item.get("percent_complete", 0)
        act = item.get("actual_hours", 0) or 0
        est = item.get("estimated_hours", 0) or 0
        wbs = item.get("wbs", "")
        name = item.get("name", "")
        start = item.get("start_date", "—")
        end = item.get("end_date", "—")
        deps = item.get("dependencies", [])
        task_type = item.get("type", "task")
        resource_names = get_resource_names(item)

        if pct == 100:
            icon = "✅"
        elif pct > 0:
            icon = "🔧"
        else:
            icon = "⬜"

        type_badge = "🔷 " if task_type == "milestone" else ""
        res_str = ", ".join(resource_names[:3]) if resource_names else "Unassigned"

        label = f"{icon} {type_badge}{wbs} {name} — {pct}% | {act:.1f}h | {res_str}"

        with st.expander(label, expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**WBS:** {wbs}")
                st.markdown(f"**Type:** {task_type.title()}")
                st.markdown(f"**Progress:** {pct}%")
            with c2:
                st.markdown(f"**Actual Hours:** {act:.1f}h")
                st.markdown(f"**Estimated Hours:** {est:.1f}h")
                if est > 0:
                    ratio = act / est * 100
                    color = "green" if ratio <= 120 else ("orange" if ratio <= 150 else "red")
                    st.markdown(f"**Hour Ratio:** :{color}[{ratio:.0f}%]")
            with c3:
                st.markdown(f"**Start:** {start or '—'}")
                st.markdown(f"**End:** {end or '—'}")
                st.markdown(f"**Tracked Time:** {'Yes' if item.get('has_tracked_time') else 'No'}")

            if resource_names:
                st.markdown(f"**Assigned ({len(resource_names)}):** {', '.join(resource_names)}")
            else:
                st.markdown("**Assigned:** :red[Unassigned]")

            if deps:
                dep_strs = []
                for d in deps:
                    if isinstance(d, dict):
                        dep_strs.append(f"{d.get('name', d.get('id', '?'))} ({d.get('type', 'FS')})")
                    else:
                        dep_strs.append(str(d))
                st.markdown(f"**Dependencies:** {', '.join(dep_strs)}")

    def render_node(item, depth=0):
        indent = "&nbsp;" * (depth * 6)

        if item.get("type") in ("group", "subgroup"):
            children = item.get("children", [])
            tasks_in_group = get_tasks_recursive(children)
            total_act = sum(t.get("actual_hours", 0) or 0 for t in tasks_in_group)

            if tasks_in_group:
                avg_progress = sum(t.get("percent_complete", 0) for t in tasks_in_group) / len(tasks_in_group)
            else:
                avg_progress = 0

            completed_count = len([t for t in tasks_in_group if t.get("percent_complete", 0) == 100])
            emoji = get_status_emoji(avg_progress, config["on_track_progress"], config["at_risk_progress"])
            name = item.get("name", "Unknown")

            # Top-level groups get gold, subgroups get lighter color
            color = "#F6AE2D" if item.get("type") == "group" else "#2E86AB"
            st.markdown(f"""
            {indent} <span style="color:{color}; font-weight:600;">▼ {name}</span>
            <span style="color:#8899AA;">({avg_progress:.0f}% complete) {emoji}</span>
            <br>{indent}&nbsp;&nbsp;&nbsp;
            <span style="color:#556677; font-size:12px;">Actual: {total_act:.1f}h | Tasks: {len(tasks_in_group)} ({completed_count} done)</span>
            """, unsafe_allow_html=True)

            if expand_all:
                for child in children:
                    render_node(child, depth + 1)

        elif item.get("type") in ("task", "milestone"):
            pct = item.get("percent_complete", 0)
            if not show_completed and pct == 100:
                return
            render_task_detail(item)

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
    total_act = sum((t.get("actual_hours", 0) or 0) for t in all_tasks)
    overall_progress = sum(t.get("percent_complete", 0) for t in all_tasks) / max(len(all_tasks), 1)
    emoji = get_status_emoji(overall_progress, config["on_track_progress"], config["at_risk_progress"])

    completed_total = len([t for t in all_tasks if t.get("percent_complete", 0) == 100])

    st.markdown(f"""
    <h3 style="color:#F6AE2D;">▼ 1.0 {project_name} ({overall_progress:.0f}% complete) {emoji}</h3>
    <span style="color:#8899AA;">Actual: {total_act:,.1f}h | Teams: {len(data)} | Tasks: {len(all_tasks)} ({completed_total} done)</span>
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
