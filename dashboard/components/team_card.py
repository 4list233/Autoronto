"""
Reusable team card component for Streamlit.
"""
import streamlit as st


def render_team_card(team, clickable=True):
    """Render a styled team performance card."""
    progress = team["progress"]
    if progress >= 75:
        border_color = "#2ECC71"
        status_emoji = "🟢"
    elif progress >= 50:
        border_color = "#F39C12"
        status_emoji = "🟡"
    else:
        border_color = "#E74C3C"
        status_emoji = "🔴"

    lead_names = ", ".join(team.get("leads", [])[:2]) or "Unassigned"

    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #1E2A3A 0%, #162230 100%);
        border-left: 4px solid {border_color};
        border-radius: 8px;
        padding: 16px;
        margin: 6px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h4 style="margin:0; color:#F6AE2D; font-size:15px;">{status_emoji} {team['name']}</h4>
            <span style="font-size:20px; font-weight:bold; color:white;">{progress:.0f}%</span>
        </div>
        <p style="margin:4px 0 8px; color:#8899AA; font-size:12px;">Lead: {lead_names}</p>
        <div style="background:#0E1117; border-radius:4px; height:8px; overflow:hidden; margin-bottom:8px;">
            <div style="background:{border_color}; height:100%; width:{min(progress, 100):.0f}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; color:#8899AA; font-size:11px;">
            <span>Hours: {team['actual_hours']:.0f}h logged</span>
            <span>Tasks: {team['completed']}/{team['total_tasks']}</span>
            <span>{team['member_count']} members</span>
        </div>
        <div style="margin-top:6px;">
            <span style="
                background: {border_color}22;
                color: {border_color};
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            ">{team['status']}</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
