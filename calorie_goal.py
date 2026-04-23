##############################################################################
# calorie_goal.py
#
# Component for setting a calorie burn goal and tracking progress.
# Displays daily or weekly progress based on user-selected goal type.
#
##############################################################################
 
import streamlit as st
from datetime import datetime, timedelta
 
def _get_today_calories(workouts: list) -> float:
    """Sum calories burned across all workouts that occurred today (UTC)."""
    today = datetime.utcnow().date()
    return sum(
        w.get("calories_burned", 0)
        for w in workouts
        if _parse_date(w.get("timestamp")) == today
    )
 
 
def _get_week_calories(workouts: list) -> float:
    """Sum calories burned across all workouts in the current ISO week (UTC)."""
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    return sum(
        w.get("calories_burned", 0)
        for w in workouts
        if week_start <= _parse_date(w.get("timestamp")) <= today
    )
 
 
def _parse_date(timestamp):
    """Safely parse a timestamp string or datetime to a date object."""
    if timestamp is None:
        return datetime.utcnow().date()
    if isinstance(timestamp, datetime):
        return timestamp.date()
    try:
        return datetime.fromisoformat(str(timestamp)).date()
    except ValueError:
        return datetime.utcnow().date()
 
 
def _calories_burned(workouts: list, goal_type: str) -> float:
    """Return daily or weekly burned calories based on goal_type."""
    if goal_type == "Daily":
        return _get_today_calories(workouts)
    return _get_week_calories(workouts)
 
@st.dialog("Edit Calorie Goal")
def _edit_goal_dialog():
    """Pop-up dialog for editing goal type and calorie target."""
    st.subheader("Set Your Calorie Burn Goal")
 
    goal_type = st.radio(
        "Goal period",
        options=["Daily", "Weekly"],
        index=0 if st.session_state.calorie_goal_type == "Daily" else 1,
        horizontal=True,
        key="dialog_goal_type",
    )
 
    calories = st.number_input(
        "Calorie target (cal)",
        min_value=0,
        max_value=10_000,
        value=int(st.session_state.calorie_goal_target),
        step=50,
        key="dialog_goal_calories",
    )
 
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save", type="primary", use_container_width=True):
            st.session_state.calorie_goal_type = goal_type
            st.session_state.calorie_goal_target = calories
            st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
 
def display_calorie_goal(workouts: list):
    """
    Render the Calorie Goal card with:
      - current progress bar (daily or weekly)
      - an 'Edit Goal' button that opens a dialog
    
    Call from activity_page.py or app.py after importing this module.
    """
 
    if "calorie_goal_target" not in st.session_state:
        st.session_state.calorie_goal_target = 500
    if "calorie_goal_type" not in st.session_state:
        st.session_state.calorie_goal_type = "Daily"
 
    goal_target: float = st.session_state.calorie_goal_target
    goal_type: str = st.session_state.calorie_goal_type
 
    burned = _calories_burned(workouts, goal_type)
    progress = min(burned / goal_target, 1.0) if goal_target > 0 else 0.0
    pct = int(progress * 100)
 
    st.subheader("Progress")
 
    with st.container(border=True):
        col_label, col_btn = st.columns([3, 1])
 
        with col_label:
            st.markdown("**Calorie Goal**")
            period_label = "Today" if goal_type == "Daily" else "This Week"
            st.caption(f"{period_label}: {int(burned)} / {int(goal_target)} cal burned")
 
        with col_btn:
            if st.button("Edit Goal", key="open_edit_goal_dialog", use_container_width=True):
                _edit_goal_dialog()
 
        st.progress(progress, text=f"{pct}% complete")
 
        if pct >= 100:
            st.success("🎉 Goal crushed! Great work.")
        elif pct >= 75:
            st.info(f"💪 Almost there — {int(goal_target - burned)} cal to go!")
        elif pct >= 50:
            st.info(f"🔥 Halfway done — keep it up!")
        else:
            remaining = int(goal_target - burned)
            st.caption(f"{remaining} cal remaining to hit your {goal_type.lower()} goal.")