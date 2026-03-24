#############################################################################
# activity_page_test.py
#
# This file contains tests for activity_page.py.
#############################################################################

import unittest
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

class TestDisplayActivityPage(unittest.TestCase):

    def setUp(self):
        self.mock_workouts = [
            {
                "workout_id": "workout0",
                "start_timestamp": "2024-01-01 00:00:00",
                "end_timestamp": "2024-01-01 00:30:00",
                "start_lat_lng": [1.5, 4.5],
                "end_lat_lng": [1.6, 4.6],
                "distance": 9.1,
                "steps": 15005,
                "calories_burned": 20,
            }
        ]

    def test_page_title_renders(self):
        """Verifies the page title is rendered."""
        def app():
            import streamlit as st
            from activity_page import display_activity_page
            workouts = st.secrets["mock_workouts"]
            display_activity_page("user1", workouts)

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()
        self.assertEqual(at.title[0].value, "My Activity")

    def test_post_content_string(self):
        """Verifies post content is constructed correctly from workout data."""
        latest = self.mock_workouts[-1]
        steps = latest.get('steps', 0)
        distance = latest.get('distance', 0)
        calories = latest.get('calories_burned', 0)

        post_content = f"Crushed it today — {steps} steps, {distance} miles, {calories} cal burned!"

        self.assertIn(str(steps), post_content)
        self.assertIn(str(distance), post_content)
        self.assertIn(str(calories), post_content)

    def test_no_workouts_shows_fallbacks(self):
        """Verifies fallback messages from submodules are shown when workouts is empty."""
        def app():
            from activity_page import display_activity_page
            display_activity_page("user1", [])

        at = AppTest.from_function(app).run()
        self.assertFalse(at.exception)

        all_info = [i.value for i in at.info]
        self.assertIn("No recent workouts yet.", all_info)

        all_text = [t.value for t in at.text]
        self.assertIn("No workout history found.", all_text)