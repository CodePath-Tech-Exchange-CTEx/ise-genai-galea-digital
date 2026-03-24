import streamlit as st
from datetime import datetime
from google.cloud import bigquery
from modules import display_recent_workouts, display_activity_summary
import uuid

def display_activity_page(user_id, workouts):
    st.title("My Activity")

    display_recent_workouts(workouts[-3:])

    display_activity_summary(workouts)

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