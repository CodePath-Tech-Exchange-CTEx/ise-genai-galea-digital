#############################################################################
# community_page_test.py
#
# This file contains tests for community_page.py.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

class TestDisplayCommunityPage(unittest.TestCase):

    def setUp(self):
        # Mock data
        self.mock_advice = {
            "timestamp": "2026-03-24 10:00:00",
            "content": "Keep pushing, you're doing great!",
            "image": None
        }
        
        self.mock_posts = [
            {
                "user_id": f"friend{i}",
                "timestamp": f"2026-03-24 09:0{i}:00",
                "content": f"Finished workout #{i}!",
                "post_image": None
            } for i in range(5) # Testing with 5 posts to verify loop
        ]

    @patch("google.cloud.bigquery.Client")
    @patch("data_fetcher.get_genai_advice")
    def test_page_title_renders(self, mock_get_advice, mock_bq_client):
        """Verifies the page title and GenAI encouragement render."""
        mock_get_advice.return_value = self.mock_advice
        
        # Setup the BigQuery mock to return our fake posts
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = self.mock_posts
        mock_bq_client.return_value.query.return_value = mock_query_job

        def app():
            import streamlit as st
            from community_page import display_community_page
            display_community_page("user1")

        at = AppTest.from_function(app).run()
        
        # Verify Titles
        self.assertEqual(at.title[0].value, "Community Hub")
        # Verify GenAI Encouragement (using header from display_genai_advice module)
        self.assertEqual(at.header[0].value, "GenAI Coach Insight")
        self.assertIn("Keep pushing", at.info[0].value)

    @patch("google.cloud.bigquery.Client")
    @patch("data_fetcher.get_genai_advice")
    def test_friend_posts_render(self, mock_get_advice, mock_bq_client):
        """Verifies that friend posts are displayed correctly."""
        mock_get_advice.return_value = self.mock_advice
        
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = self.mock_posts
        mock_bq_client.return_value.query.return_value = mock_query_job

        def app():
            from community_page import display_community_page
            display_community_page("user1")

        at = AppTest.from_function(app).run()
        
        # Combine all markdown to check for friend IDs and content
        all_md = " ".join([m.value for m in at.markdown])
        for i in range(5):
            self.assertIn(f"friend{i}", all_md)
            self.assertIn(f"Finished workout #{i}!", all_md)

    @patch("google.cloud.bigquery.Client")
    @patch("data_fetcher.get_genai_advice")
    def test_no_friends_shows_info_message(self, mock_get_advice, mock_bq_client):
        """Verifies fallback message when no friend posts are found."""
        mock_get_advice.return_value = self.mock_advice
        
        # Mock BigQuery returning an empty list
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_bq_client.return_value.query.return_value = mock_query_job

        def app():
            from community_page import display_community_page
            display_community_page("user1")

        at = AppTest.from_function(app).run()
        
        all_info = [i.value for i in at.info]
        self.assertIn("No posts from friends yet. Go set a PR and share it!", all_info)

if __name__ == "__main__":
    unittest.main()