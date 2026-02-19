#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

from datetime import datetime
from internals import create_component
import pandas as pd
import streamlit as st


# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass


def display_activity_summary(workouts_list):
    """Displays an 'activity summary' that showcases data about the user's
    latest workout.

    Args:
        workouts_list: the list of the user's workouts 
    """
    st.header("Activity Summary")

    if not workouts_list:
        st.text("No workout history found.")
        return

    latest_workout = workouts_list[-1]
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    start = datetime.strptime(latest_workout['start_timestamp'], DATE_FORMAT)
    end = datetime.strptime(latest_workout['end_timestamp'], DATE_FORMAT)

    st.caption(start.strftime('%B %d, %Y'))

    latest_workout_duration_mins = int((end - start).total_seconds() / 60)

    # Metrics
    cols = st.columns(4)
    metrics = [
        ("Duration", f"{latest_workout_duration_mins} mins"),
        ("Total Steps", latest_workout.get('steps', 0)),
        ("Distance", f"{latest_workout.get('distance', 0)} mi"),
        ("Calories Burned", f"{latest_workout.get('calories_burned', 0)} cal")
    ]

    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value, border=True)

    # Coordinate Map
    start_coords = latest_workout['start_lat_lng']
    end_coords = latest_workout['end_lat_lng']

    map_data = pd.DataFrame([
        {"lat": start_coords[0], "lon": start_coords[1], "name": "Start"},
        {"lat": end_coords[0], "lon": end_coords[1], "name": "End"}
    ])
    st.map(map_data)


def display_recent_workouts(workouts_list):
    """Write a good docstring here."""
    pass


def display_genai_advice(timestamp, content, image):
    """Write a good docstring here."""
    pass
