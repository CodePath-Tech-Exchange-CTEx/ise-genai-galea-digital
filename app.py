#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

userId = 'user1'

workouts = get_user_workouts(userId)
genai_advice = get_genai_advice(userId)


def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # An example of displaying a custom component called "my_custom_component"
    value = st.text_input('Enter your name')
    display_my_custom_component(value)
    display_post(
        username="WorkoutWarrior",
        user_image="https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png?20170328184010", 
        timestamp="2024-01-01 00:00:00",
        content="Crushed my morning run! Feeling great.",
        post_image="https://firstbenefits.org/wp-content/uploads/2017/10/placeholder.png"
    )
    display_activity_summary(workouts)
    display_recent_workouts(workouts)
    display_genai_advice(
        genai_advice['timestamp'],
        genai_advice['content'],
        genai_advice['image']
    )



# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()
