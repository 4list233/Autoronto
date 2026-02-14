"""
Page 6: Utilization & Contribution
Track hour logging trends and identify over/under-contributing members.
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_hierarchical_data, get_all_tasks, get_teams, get_all_resources, load_config
from utils.outlier_detection import detect_outliers
from components.charts import resource_hours_chart, hours_comparison_chart


def render():
    data = load_hierarchical_data()
    all_tasks = get_all_tasks(data)
    teams = get_teams(data)
    resources = get_all_resources(data)
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>📈 Utilization & Member Contributions</h1>
        <p>Track hour logging, identify over/under-contributing members | WBS Resource Tracking</p>
    </div>
    """, unsafe_allow_html=True)

    # Top metrics (actual hours only, no expected)
    total_hours = sum(t["actual_hours"] for t in all_tasks)
    total_members = len(resources)
    active_members = len([r for r in resources if r["total_hours"] > 0])
    avg_per_active = total_hours / max(active_members, 1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{total_hours:.0f}h</div>
            <div class="label">Total Hours Logged</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{active_members}/{total_members}</div>
            <div class="label">Active Members</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card compact-metric">
            <div class="value">{avg_per_active:.1f}h</div>
            <div class="label">Avg per Active Member</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Top contributors chart
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Top Contributors")
    st.plotly_chart(resource_hours_chart(resources, top_n=20), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Outlier detection
    outliers = detect_outliers(resources, config)

    col_under, col_over = st.columns(2)

    with col_under:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"#### 🔴 Under-Contributing (< {config['low_hour_member']}h threshold)")
        if outliers["under"]:
            rows = []
            for o in sorted(outliers["under"], key=lambda x: x["total_hours"]):
                rows.append({
                    "Name": o["name"],
                    "Role": o["role"],
                    "Hours": f"{o['total_hours']:.1f}h",
                    "Threshold": f"{o['threshold']}h",
                    "Deficit": f"-{o['deficit']}h",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.success("No under-contributing members detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_over:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"#### 🟠 Over-Contributing (> {config['high_hour_member']}h threshold)")
        if outliers["over"]:
            rows = []
            for o in sorted(outliers["over"], key=lambda x: -x["total_hours"]):
                rows.append({
                    "Name": o["name"],
                    "Role": o["role"],
                    "Hours": f"{o['total_hours']:.1f}h",
                    "Threshold": f"{o['threshold']}h",
                    "Surplus": f"+{o['surplus']}h",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.success("No over-contributing members detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Team efficiency comparison
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Team Hours Comparison")
    st.plotly_chart(hours_comparison_chart(teams), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # WBS Integration Note
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-card" style="border:1px solid #2E86AB;">
        <h4 style="color:#2E86AB;">WBS Resource Utilization Tracking</h4>
        <p style="color:#8899AA; font-size:13px;">
            Per SAE ADCII rules, the WBS must include <b>hrs/wk per person</b> assigned to each deliverable.
            This page surfaces that data directly from TeamGantt time blocks.
            The PM can use this to identify over/underutilized team members and rebalance workload —
            a key element of WBS proficiency evaluated by judges.
        </p>
    </div>
    """, unsafe_allow_html=True)
