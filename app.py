#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts
from activity_page import display_activity_page
from community_page import display_community_page

userId = 'user1'

genai_advice = get_genai_advice(userId)
posts = get_user_posts(userId)
workouts = get_user_workouts(userId)

def display_app_page():
    """Displays the home page of the app."""
    st.title('GALEA Digital\'s Workout App')

    # TODO: Update display_post to properly handle data from database
    display_post(
        username=posts[0]['user_id'],
        user_image=None, 
        timestamp=posts[0]['timestamp'],
        content=posts[0]['content'],
        post_image=None
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
    home = st.Page(display_app_page, title="Home", icon="🏠")
    activity = st.Page(lambda: display_activity_page(userId, workouts), title="My Activity", icon="🏃", url_path="activity")
    community = st.Page(lambda: display_community_page(userId), title="Community", icon="👥", url_path="community")

    pg = st.navigation({
        "GALEA Digital's Workout App": [home, activity, community]
    })
    pg.run()
