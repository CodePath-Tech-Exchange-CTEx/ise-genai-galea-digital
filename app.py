#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts, get_username
from activity_page import display_activity_page
from community_page import display_community_page

userId = 'user1'
username = get_username(userId)

# Fetch data
genai_advice = get_genai_advice(userId)
posts = get_user_posts(userId)
workouts = get_user_workouts(userId)

def compact_divider():
    st.markdown('<hr style="margin: 0px; border: 0.5px solid #ddd;">', unsafe_allow_html=True)

def display_app_page():
    st.header(f"Welcome Back, {username}!")
    
    # Create two columns
    col_main, col_side = st.columns([2, 1], gap="medium")
    
    with col_main:
        compact_divider()

        display_genai_advice(
            genai_advice['timestamp'],
            genai_advice['content'],
            genai_advice['image']
        )
        compact_divider()
        
        st.write("### Most Recent Post")
        display_post(
            username=get_username(posts[0]['user_id']),
            user_image=None, 
            timestamp=posts[0]['timestamp'],
            content=posts[0]['content'],
            post_image=None
        )
        compact_divider()


    with col_side:
        compact_divider()

        if workouts:
            display_recent_workouts([workouts[-1]]) # Only pass the last one

        if st.button("View Full Activity 🏃"):
            st.switch_page(activity)
        if st.button("See Community Progress 👥"):
            st.switch_page(community)
        
        compact_divider()
        

if __name__ == '__main__':
    home = st.Page(display_app_page, title="Home", icon="🏠")
    activity = st.Page(lambda: display_activity_page(userId, workouts), title="Activity", icon="🏃", url_path="activity")
    community = st.Page(lambda: display_community_page(userId), title="Community", icon="👥", url_path="community")

    pg = st.navigation({"Pages": [home, activity, community]})

    # Dynamic Browser Tab Title
    st.set_page_config(page_title=f"GALEA DIGITAL | {pg.title}", layout="wide")

    # CUSTOM CSS: Tightening margins and the divider
    st.markdown("""
        <style>
               .block-container { 
                    padding-top: 1.5rem;
                    padding-left: 20rem;
                    padding-right: 20rem;
                }
               h1 { margin-bottom: 0px !important; padding-bottom: 5px !important; }
               h3 { margin-top: 10px !important; }
        </style>
        """, unsafe_allow_html=True)

    # Global Header
    st.title('GALEA DIGITAL: Workout App')
    compact_divider()

    pg.run()