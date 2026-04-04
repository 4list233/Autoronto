"""
Reusable task table component for Streamlit.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.calculations import days_overdue, detect_task_issues


def render_task_table(tasks, config, show_group=True, show_issues=True):
    """Render a styled task table from a list of task dicts."""
    if not tasks:
        st.info("No tasks to display.")
        return

    rows = []
    for t in tasks:
        overdue = days_overdue(t.get("end_date"))
        issues = detect_task_issues(t, config) if show_issues else []

        deadline_str = t.get("end_date", "—")
        if overdue > 7:
            deadline_str += " ⚠️⚠️"
        elif overdue > 0:
            deadline_str += " ⚠️"

        if issues and any("CRITICAL" in i for i in issues):
            status_icon = "🔴"
        elif issues:
            status_icon = "🟡"
        else:
            status_icon = "⚪"

        row = {
            "": status_icon,
            "Task": t.get("name", ""),
            "Progress": f"{t.get('percent_complete', 0)}%",
            "Act. Hours": t.get("actual_hours", 0),
            "Deadline": deadline_str,
            "Assignees": ", ".join(t.get("resources", [])[:3]),
        }
        if show_group:
            row["Team"] = t.get("group", "")
        if show_issues:
            row["Issues"] = "; ".join(issues) if issues else "—"

        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(400, len(rows) * 38 + 38),
    )
