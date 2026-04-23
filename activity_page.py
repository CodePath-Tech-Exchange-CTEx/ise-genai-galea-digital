import streamlit as st
from datetime import datetime
from google.cloud import bigquery
from modules import display_recent_workouts, display_activity_summary
from workout_feedback import initialize_feedback_state, get_feedback_button_label, render_feedback_form
from calorie_goal import display_calorie_goal
import uuid

def display_activity_page(user_id, workouts):
    st.title("My Activity")

    initialize_feedback_state()
    displayed_workouts = workouts[-3:] if workouts else []

    display_recent_workouts(
        displayed_workouts,
        feedback_by_workout=st.session_state["workout_feedback"]
    )

    if displayed_workouts:
        button_label = get_feedback_button_label(displayed_workouts)

        if st.button(button_label):
            st.session_state["show_feedback_form"] = True

        if st.session_state["show_feedback_form"]:
            render_feedback_form(displayed_workouts)


    display_activity_summary(workouts)

    display_calorie_goal(workouts)

    if workouts:
        latest = workouts[-1]
        steps = latest.get('steps', 0)
        distance = latest.get('distance', 0)
        calories = latest.get('calories_burned', 0)
        post_content = f"Crushed it today — {steps} steps, {distance} miles, {calories} cal burned!"

        @st.dialog("Share to Community")
        def share_dialog():
            edited_content = st.text_area(
                "Edit your post before sharing:",
                value=post_content,
                height=100
            )
            st.caption(datetime.utcnow().strftime("%B %d, %Y"))

            if st.button("Confirm & Post"):
                # TODO: abstract this into an insert_post() function
                client = bigquery.Client()
                table_id = "amier-davis-hu.ISE.Posts"

                row = [{
                    "PostId": str(uuid.uuid4()),
                    "AuthorId": user_id,
                    "Timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "ImageUrl": None,
                    "Content": edited_content
                }]

                errors = client.insert_rows_json(table_id, row)

                if errors:
                    st.error(f"Failed to post: {errors}")
                else:
                    st.success("Posted to the community!")
                    st.rerun()

        if st.button("Share to Community"):
            share_dialog()