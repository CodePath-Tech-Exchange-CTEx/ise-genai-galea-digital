#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def setUp(self):
        """Define reusable mock data for workouts. Define scripts to create an
        isolated testing environment.
        """
        self.mock_workouts = [
            {
                "start_timestamp": "2026-02-19 10:00:00",
                "end_timestamp": "2026-02-19 10:45:00",
                "steps": 5000,
                "distance": 2.5,
                "calories_burned": 350,
                "start_lat_lng": [34.0522, -118.2437],
                "end_lat_lng": [34.0522, -118.2437]
            }
        ]
        self.empty_workout_script = """
            import streamlit as st
            from modules import display_activity_summary
            display_activity_summary([])
        """
        self.populated_workout_script = f"""
            import streamlit as st
            from modules import display_activity_summary
            display_activity_summary({self.mock_workouts})
        """

    def test_empty_workout_list(self):
        """Verifies fallback message when no workout data is provided."""
        at = AppTest.from_string(self.empty_workout_script).run()
        
        print(at.header[0].value)
        print(at.text[0].value)
        assert at.header[0].value == "Activity Summary"
        assert at.text[0].value == "No workout history found."
        assert len(at.metric) == 0

    def test_metrics_rendering(self):
        """Verifies that workout duration and metrics are calculated and displayed correctly."""
        at = AppTest.from_string(self.populated_workout_script).run()

        assert at.caption[0].value == "February 19, 2026"

        assert at.metric[0].label == "Duration"
        assert at.metric[0].value == "45 mins"
        
        assert at.metric[1].label == "Total Steps"
        assert at.metric[1].value == "5000"

        assert at.metric[3].label == "Calories Burned"
        assert at.metric[3].value == "350 cal"


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()
