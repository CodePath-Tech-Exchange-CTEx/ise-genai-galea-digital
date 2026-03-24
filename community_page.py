import streamlit as st
from google.cloud import bigquery
from modules import display_post, display_genai_advice
from data_fetcher import get_genai_advice

def display_community_page(user_id):
    st.title("Community Hub")

    # 1. Display GenAI Advice and Encouragement
    genai_advice = get_genai_advice(user_id)
    if genai_advice:
        display_genai_advice(
            genai_advice['timestamp'],
            genai_advice['content'],
            genai_advice['image']
        )

    st.divider()
    st.subheader("Recent Activity from Friends")

    # 2. Fetch First 10 Friend Posts directly
    client = bigquery.Client()
    
    # JOIN the Posts table with a Friends table to get only social circle content
    # Use ORDER BY + LIMIT 10 to satisfy the assignment requirements.
    query = f"""
        SELECT 
            p.AuthorId as user_id,
            p.Timestamp as timestamp,
            p.Content as content,
            p.ImageUrl as post_image
        FROM `amier-davis-hu.ISE.Posts` p
        JOIN `amier-davis-hu.ISE.Friends` f ON p.AuthorId = f.friend_id
        WHERE f.user_id = '{user_id}'
        ORDER BY p.Timestamp DESC
        LIMIT 10
    """

    try:
        query_job = client.query(query)
        posts = query_job.result()
        
        post_list = [dict(row) for row in posts]

        if not post_list:
            st.info("No posts from friends yet. Go set a PR and share it!")
        else:
            for post in post_list:
                ts = post['timestamp']
                if hasattr(ts, 'strftime'):
                    ts = ts.strftime("%Y-%m-%d %H:%M:%S")

                display_post(
                    username=post['user_id'],
                    user_image=None, 
                    timestamp=ts,
                    content=post['content'],
                    post_image=post['post_image']
                )
    except Exception as e:
        st.error(f"Error loading community feed: {e}")