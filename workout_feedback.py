import streamlit as st


FEEDBACK_CSS = """
<style>
.effort-label-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.35rem;
    font-weight: 600;
    font-size: 0.95rem;
    color: #374151;
}

div[data-testid="stPills"] [data-baseweb="tag"] {
    border-radius: 12px !important;
    padding: 0.55rem 0.95rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border: 1px solid #d1d5db !important;
    background: #f8fafc !important;
    color: #111827 !important;
}

div[data-testid="stPills"] [data-baseweb="tag"]:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
}

div[data-testid="stPills"] [aria-selected="true"][data-baseweb="tag"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border-color: transparent !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.22) !important;
}
</style>
"""


def initialize_feedback_state():
    """Initialize feedback-related session state."""
    if "workout_feedback" not in st.session_state:
        st.session_state["workout_feedback"] = {}

    if "show_feedback_form" not in st.session_state:
        st.session_state["show_feedback_form"] = False

    if "feedback_css_loaded" not in st.session_state:
        st.session_state["feedback_css_loaded"] = False


def load_feedback_css():
    """Inject feedback CSS once per session."""
    if not st.session_state["feedback_css_loaded"]:
        st.markdown(FEEDBACK_CSS, unsafe_allow_html=True)
        st.session_state["feedback_css_loaded"] = True


def render_effort_selector(widget_key):
    """Render the styled effort selector."""
    st.markdown("### Effort")
    st.caption("Select one")

    st.markdown(
        '<div class="effort-label-row"><span>Easy</span><span>Hard</span></div>',
        unsafe_allow_html=True
    )

    return st.pills(
        "Effort level",
        options=list(range(1, 10)),
        selection_mode="single",
        key=widget_key,
        label_visibility="collapsed",
        width="stretch",
    )


def get_feedback_button_label(displayed_workouts):
    """Return Add Feedback or Edit Feedback depending on existing feedback."""
    displayed_workout_ids = [
        w.get("workout_id", f"workout_{i}")
        for i, w in enumerate(displayed_workouts)
    ]

    has_existing_feedback = any(
        workout_id in st.session_state["workout_feedback"]
        for workout_id in displayed_workout_ids
    )

    return "Edit Feedback" if has_existing_feedback else "Add Feedback"


def render_feedback_form(displayed_workouts):
    """Render the feedback form and save results to session state."""
    load_feedback_css()
    st.subheader("Feedback Form")

    workout_options = {}
    for i, workout in enumerate(displayed_workouts):
        workout_id = workout.get("workout_id", f"workout_{i}")
        label = f"Workout {i + 1}"
        workout_options[label] = workout_id

    with st.form("workout_feedback_form"):
        selected_workout_label = st.radio(
            "Select the workout you want to give feedback for:",
            options=list(workout_options.keys())
        )
        selected_workout_id = workout_options[selected_workout_label]

        existing_feedback = st.session_state["workout_feedback"].get(
            selected_workout_id, {}
        )

        effort_widget_key = f"effort_pills_{selected_workout_id}"
        motivation_widget_key = f"motivation_{selected_workout_id}"
        notes_widget_key = f"notes_{selected_workout_id}"

        if effort_widget_key not in st.session_state:
            st.session_state[effort_widget_key] = existing_feedback.get("effort", None)

        if motivation_widget_key not in st.session_state:
            st.session_state[motivation_widget_key] = existing_feedback.get("motivation", "🙂")

        if notes_widget_key not in st.session_state:
            st.session_state[notes_widget_key] = existing_feedback.get("notes", "")

        effort = render_effort_selector(effort_widget_key)

        st.markdown("### Motivation")
        motivation = st.radio(
            "Choose one",
            options=["😞", "😐", "🙂", "😁"],
            horizontal=True,
            key=motivation_widget_key
        )

        notes = st.text_area(
            "Notes",
            placeholder="Write your feedback here...",
            key=notes_widget_key
        )

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Submit Feedback")
        with col2:
            cancel = st.form_submit_button("Cancel")

    if cancel:
        st.session_state["show_feedback_form"] = False
        st.rerun()

    if submit:
        if effort is None:
            st.warning("Please select an effort level.")
        else:
            st.session_state["workout_feedback"][selected_workout_id] = {
                "effort": effort,
                "motivation": motivation,
                "notes": notes
            }
            st.session_state["show_feedback_form"] = False
            st.success("Feedback saved!")
            st.rerun()