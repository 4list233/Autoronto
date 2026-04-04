"""
Reusable week selector component for weekly views.
"""
import streamlit as st
from datetime import date


def render_week_selector(available_weeks, key="week_selector"):
    """
    Render a week selector dropdown.
    
    Args:
        available_weeks: List of week dicts from get_available_weeks()
        key: Unique key for this selector
    
    Returns:
        Selected week_start (date object)
    """
    week_options = [w["label"] for w in available_weeks]
    
    # Find current week as default
    default_idx = 0
    for i, w in enumerate(available_weeks):
        if w.get("is_current"):
            default_idx = i
            break
    
    selected_label = st.selectbox(
        "Week:",
        options=week_options,
        index=default_idx,
        key=key
    )
    
    # Return the week_start date for the selected label
    for w in available_weeks:
        if w["label"] == selected_label:
            return w["start"]
    
    return available_weeks[0]["start"]


def render_week_navigation(available_weeks, current_idx, key_prefix="week_nav"):
    """
    Render Previous/Next week navigation buttons.
    
    Args:
        available_weeks: List of week dicts
        current_idx: Current week index
        key_prefix: Prefix for button keys
    
    Returns:
        New week index or current_idx if no change
    """
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("◀ Previous Week", key=f"{key_prefix}_prev", disabled=current_idx == 0):
            return current_idx - 1
    
    with col2:
        st.markdown(f"<div style='text-align:center; padding:8px;'><b>{available_weeks[current_idx]['label']}</b></div>", 
                    unsafe_allow_html=True)
    
    with col3:
        if st.button("Next Week ▶", key=f"{key_prefix}_next", disabled=current_idx >= len(available_weeks) - 1):
            return current_idx + 1
    
    return current_idx
