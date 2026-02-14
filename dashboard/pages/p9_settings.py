"""
Page 9: Settings (PM Access Only)
Configure all dashboard thresholds and parameters from a single page.
All values are persisted to config.json and used across every page.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.data_loader import load_config, save_config
from utils.api_client import is_api_available, sync_all


def render():
    config = load_config()

    st.markdown("""
    <div class="dashboard-header">
        <h1>⚙️ Dashboard Configuration</h1>
        <p>PM Access Only — All thresholds are modular and persist to config.json</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-card" style="border:1px solid #F6AE2D44; margin-bottom:16px;">
        <p style="color:#F6AE2D; margin:0;">All settings on this page are stored in a single <b>config.json</b> file.
        Every page in the dashboard reads from this config, making all thresholds fully modular and adjustable at runtime by the PM.</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- Data Source Toggle ----
    st.markdown('<div class="metric-card" style="margin-bottom:16px; border:1px solid #2E86AB;">', unsafe_allow_html=True)
    st.markdown("#### ⚡ Data Source")
    api_ok = is_api_available()
    current_source = config.get("data_source", "cached")

    col_ds1, col_ds2 = st.columns([2, 1])
    with col_ds1:
        data_source = st.radio(
            "Where should the dashboard read data from?",
            ["cached", "live"],
            index=0 if current_source == "cached" else 1,
            format_func=lambda x: {
                "cached": "📁 Cached (local JSON files in data/)",
                "live": "🌐 Live (TeamGantt API — real-time)",
            }[x],
            key="data_source_radio",
            help="Live mode calls the TeamGantt API on every page load. Cached mode reads from local files (faster, works offline).",
            horizontal=True,
        )
    with col_ds2:
        st.markdown(f"""
        <div style="padding:8px; text-align:center;">
            <span style="color:{'#2ECC71' if api_ok else '#E74C3C'}; font-weight:600;">
                {'✅ API Token Found' if api_ok else '❌ No API Token'}
            </span>
            <br><span style="color:#8899AA; font-size:11px;">
                {'Set in .env as TEAMGANTT_TOKEN' if not api_ok else 'Reading from .env'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Sync button
    col_sync1, col_sync2 = st.columns(2)
    with col_sync1:
        if st.button("🔄 Sync Now — Pull Latest from API", use_container_width=True, disabled=not api_ok):
            with st.spinner("Fetching from TeamGantt API..."):
                results = sync_all()
            for key, val in results.items():
                if val["status"] == "ok":
                    st.success(f"{key}: synced OK" + (f" ({val.get('count', '')} items)" if 'count' in val else ""))
                else:
                    st.error(f"{key}: {val.get('error', 'unknown error')}")
    with col_sync2:
        st.markdown(f"""
        <div style="padding:8px; color:#8899AA; font-size:12px;">
            Sync pulls the latest hierarchical tasks, flat task list, and project metadata from the TeamGantt API
            and saves to <code>data/</code>. This updates the cached files that the dashboard reads from.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Hour allocation settings
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### 🕐 Weekly Hour Allocation")
    col1, col2 = st.columns(2)
    with col1:
        member_hrs = st.slider(
            "Member Default Hours/Week",
            min_value=5, max_value=20,
            value=config.get("member_hours_per_week", 10),
            key="member_hrs",
            help="Default weekly hours expected from regular members",
        )
    with col2:
        lead_hrs = st.slider(
            "Lead Default Hours/Week",
            min_value=8, max_value=25,
            value=config.get("lead_hours_per_week", 13),
            key="lead_hrs",
            help="Default weekly hours expected from team leads (30% premium)",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Low hour thresholds
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### 🔴 Under-Contributing Thresholds")
    col1, col2, col3 = st.columns(3)
    with col1:
        low_member = st.slider(
            "Low Hour Threshold (Members)",
            min_value=0, max_value=15,
            value=config.get("low_hour_member", 7),
            key="low_member",
            help="Members logging fewer hours than this are flagged as under-contributing",
        )
    with col2:
        low_lead = st.slider(
            "Low Hour Threshold (Leads)",
            min_value=0, max_value=20,
            value=config.get("low_hour_lead", 9),
            key="low_lead",
            help="Leads logging fewer hours than this are flagged",
        )
    with col3:
        low_weeks = st.number_input(
            "Consecutive Weeks Before Alert",
            min_value=1, max_value=4,
            value=config.get("low_hour_weeks", 2),
            key="low_weeks",
            help="Number of consecutive weeks below threshold before alert triggers",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # High hour thresholds
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### 🟠 Over-Contributing Thresholds")
    col1, col2, col3 = st.columns(3)
    with col1:
        high_member = st.slider(
            "High Hour Threshold (Members)",
            min_value=12, max_value=30,
            value=config.get("high_hour_member", 15),
            key="high_member",
            help="Members logging more hours than this are flagged as over-contributing",
        )
    with col2:
        high_lead = st.slider(
            "High Hour Threshold (Leads)",
            min_value=15, max_value=35,
            value=config.get("high_hour_lead", 20),
            key="high_lead",
            help="Leads logging more hours than this are flagged",
        )
    with col3:
        high_weeks = st.number_input(
            "Consecutive Weeks Before Alert",
            min_value=1, max_value=4,
            value=config.get("high_hour_weeks", 2),
            key="high_weeks",
            help="Number of consecutive weeks above threshold before alert triggers",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Task status thresholds
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### ⚠️ Task Alert Thresholds")
    col1, col2, col3 = st.columns(3)
    with col1:
        overdue_crit = st.number_input(
            "Overdue Critical (days)",
            min_value=1, max_value=30,
            value=config.get("overdue_critical_days", 7),
            key="overdue_crit",
            help="Tasks overdue by this many days are flagged as critical",
        )
    with col2:
        stalled_days = st.number_input(
            "Stalled Task (days no update)",
            min_value=7, max_value=60,
            value=config.get("stalled_task_days", 14),
            key="stalled_days",
            help="Tasks with no updates for this many days trigger a warning",
        )
    with col3:
        over_est = st.number_input(
            "Over Estimate % Warning",
            min_value=100, max_value=300,
            value=config.get("over_estimate_percent", 150),
            key="over_est",
            help="Tasks exceeding this % of estimated hours trigger a warning",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Team health thresholds
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### 🎯 Team Health Status Thresholds")
    col1, col2 = st.columns(2)
    with col1:
        on_track = st.slider(
            "On Track (Green) — Progress ≥",
            min_value=50, max_value=100,
            value=config.get("on_track_progress", 75),
            key="on_track",
            help="Teams with progress at or above this % show as green/on-track",
        )
    with col2:
        at_risk = st.slider(
            "At Risk (Yellow) — Progress ≥",
            min_value=20, max_value=on_track - 1,
            value=min(config.get("at_risk_progress", 50), on_track - 1),
            key="at_risk",
            help="Teams with progress at or above this % (but below green) show as yellow/at-risk. Below this = red/behind.",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Project dates
    st.markdown('<div class="metric-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
    st.markdown("#### 📅 Key Dates")
    col1, col2 = st.columns(2)
    with col1:
        comp_date = st.text_input(
            "Competition Date (YYYY-MM-DD)",
            value=config.get("competition_date", "2026-06-05"),
            key="comp_date",
        )
    with col2:
        ws_date = st.text_input(
            "Winter Workshop Date (YYYY-MM-DD)",
            value=config.get("winter_workshop_date", "2026-02-17"),
            key="ws_date",
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Save / Reset
    st.markdown("<br>", unsafe_allow_html=True)
    col_save, col_reset = st.columns(2)

    with col_save:
        if st.button("💾 Save Configuration", type="primary", use_container_width=True):
            new_config = {
                "member_hours_per_week": member_hrs,
                "lead_hours_per_week": lead_hrs,
                "low_hour_member": low_member,
                "low_hour_lead": low_lead,
                "low_hour_weeks": low_weeks,
                "high_hour_member": high_member,
                "high_hour_lead": high_lead,
                "high_hour_weeks": high_weeks,
                "overdue_critical_days": overdue_crit,
                "stalled_task_days": stalled_days,
                "over_estimate_percent": over_est,
                "on_track_progress": on_track,
                "at_risk_progress": at_risk,
                "competition_date": comp_date,
                "winter_workshop_date": ws_date,
                "project_id": config.get("project_id", "4336931"),
                "project_name": config.get("project_name", "R2Y5 - aUToronto SAE 2026"),
                "data_source": data_source,
            }
            save_config(new_config)
            st.success("Configuration saved to config.json!")
            st.rerun()

    with col_reset:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            default_config = {
                "low_hour_member": 7,
                "low_hour_lead": 9,
                "low_hour_weeks": 2,
                "high_hour_member": 15,
                "high_hour_lead": 20,
                "high_hour_weeks": 2,
                "overdue_critical_days": 7,
                "stalled_task_days": 14,
                "over_estimate_percent": 150,
                "on_track_progress": 75,
                "at_risk_progress": 50,
                "member_hours_per_week": 10,
                "lead_hours_per_week": 13,
                "project_id": "4336931",
                "project_name": "R2Y5 - aUToronto SAE 2026",
                "competition_date": "2026-06-05",
                "winter_workshop_date": "2026-02-17",
                "data_source": "live",
            }
            save_config(default_config)
            st.success("Configuration reset to defaults!")
            st.rerun()

    # Current config display
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("#### Current Configuration (config.json)")
    st.json(config)
    st.markdown('</div>', unsafe_allow_html=True)

    # API Integration info
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="metric-card" style="border:1px solid #2E86AB;">
        <h4 style="color:#2E86AB;">TeamGantt API Integration Reference</h4>
        <p style="color:#8899AA; font-size:13px;">
            <b>Data Source:</b> TeamGantt REST API (api.teamgantt.com/v1)<br>
            <b>Project:</b> R2Y5 (ID: {project_id})<br>
            <b>Endpoints:</b><br>
            • <code>GET /projects/{{id}}/children</code> — Fetch hierarchical task tree<br>
            • <code>PATCH /tasks/{{id}}</code> — Update estimated hours<br>
            • <code>POST /times</code> — Log actual hours via time blocks<br>
            • <code>GET /tasks/{{id}}</code> — Verify task status
        </p>
    </div>
    """.format(project_id=config.get("project_id", "4336931")), unsafe_allow_html=True)
