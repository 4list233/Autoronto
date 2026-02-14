"""
aUToronto PM Dashboard - Main Entry Point
Multi-page Streamlit app for R2Y5 project management.
Integrates with TeamGantt backend for live WBS and resource tracking.

Run: streamlit run dashboard/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="aUToronto PM Dashboard | R2Y5",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(180deg, #0A0F1A 0%, #0E1117 100%);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1520 0%, #0A0F1A 100%);
        border-right: 1px solid #1E2A3A;
    }

    /* Card containers */
    .metric-card {
        background: linear-gradient(135deg, #1E2A3A 0%, #162230 100%);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #2E3A4A;
    }

    /* Headers */
    .dashboard-header {
        background: linear-gradient(90deg, #1B3A5C 0%, #2E86AB 100%);
        border-radius: 10px;
        padding: 20px 28px;
        margin-bottom: 20px;
        border: 1px solid #3A5A7A;
    }

    .dashboard-header h1 {
        color: #F6AE2D;
        margin: 0;
        font-size: 28px;
    }

    .dashboard-header p {
        color: #CCDDEE;
        margin: 4px 0 0;
        font-size: 14px;
    }

    /* Status badges */
    .badge-green {
        background: #2ECC7122; color: #2ECC71;
        padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
    }
    .badge-yellow {
        background: #F39C1222; color: #F39C12;
        padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
    }
    .badge-red {
        background: #E74C3C22; color: #E74C3C;
        padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600;
    }

    /* Compact metric */
    .compact-metric {
        text-align: center;
        padding: 12px;
    }
    .compact-metric .value {
        font-size: 32px;
        font-weight: 700;
        color: #F6AE2D;
    }
    .compact-metric .label {
        font-size: 12px;
        color: #8899AA;
        margin-top: 4px;
    }

    /* Integration badge */
    .integration-badge {
        background: linear-gradient(90deg, #1B3A5C, #2E86AB);
        border-radius: 8px;
        padding: 8px 16px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: #CCDDEE;
        border: 1px solid #3A5A7A;
    }

    /* Hide default streamlit footer */
    footer { visibility: hidden; }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1E2A3A;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        color: #8899AA;
    }
    .stTabs [aria-selected="true"] {
        background: #2E86AB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:16px 0;">
        <h2 style="color:#F6AE2D; margin:0;">🏎️ aUToronto</h2>
        <p style="color:#8899AA; font-size:12px; margin:4px 0;">R2Y5 PM Dashboard</p>
        <div class="integration-badge" style="margin-top:8px;">
            <span>⚡ TeamGantt Integration</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Executive Dashboard",
            "📊 Team Performance",
            "👥 Team Detail",
            "🌳 WBS Hierarchy",
            "⚠️ At-Risk Tasks",
            "📈 Utilization",
            "👤 All Members",
            "📅 Weekly Team Summary",
            "⏱️ Hour Logging",
            "📋 Tasks Outstanding",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Show data source status
    import json, os
    _cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(_cfg_path) as _f:
        _cfg = json.load(_f)
    _src = _cfg.get("data_source", "cached")
    _src_label = "🌐 LIVE API" if _src == "live" else "📁 Cached"
    _src_color = "#2ECC71" if _src == "live" else "#F6AE2D"

    st.markdown(f"""
    <div style="color:#556677; font-size:11px; text-align:center;">
        <p>Data: <span style="color:{_src_color}; font-weight:600;">{_src_label}</span></p>
        <p>Project: R2Y5 (ID: {_cfg.get('project_id', '4336931')})</p>
        <p>SAE AutoDrive Challenge II</p>
    </div>
    """, unsafe_allow_html=True)


# Page routing — direct imports with error handling
def _run_page(page_name):
    try:
        if page_name == "🏠 Executive Dashboard":
            from pages.p1_executive import render
        elif page_name == "📊 Team Performance":
            from pages.p2_team_grid import render
        elif page_name == "👥 Team Detail":
            from pages.p3_team_detail import render
        elif page_name == "🌳 WBS Hierarchy":
            from pages.p4_wbs_hierarchy import render
        elif page_name == "⚠️ At-Risk Tasks":
            from pages.p5_at_risk import render
        elif page_name == "📈 Utilization":
            from pages.p6_utilization import render
        elif page_name == "👤 All Members":
            from pages.p10_all_members import render
        elif page_name == "📅 Weekly Team Summary":
            from pages.p11_weekly_teams import render
        elif page_name == "⏱️ Hour Logging":
            from pages.p7_hour_logging import render
        elif page_name == "📋 Tasks Outstanding":
            from pages.p8_tasks_outstanding import render
        elif page_name == "⚙️ Settings":
            from pages.p9_settings import render
        else:
            st.warning("Unknown page")
            return
        render()
    except Exception as e:
        st.error(f"**Error on {page_name}:** {e}")
        st.exception(e)

_run_page(page)
