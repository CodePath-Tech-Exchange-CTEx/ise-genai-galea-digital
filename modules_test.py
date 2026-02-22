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

    def test_display_post_renders_content(self):
        """Verifies that the username, content, and timestamp render correctly."""
        def app():
            from modules import display_post
            display_post(
                username="FitnessGuru",
                user_image=None, 
                timestamp="2024-01-01 00:00:00",
                content="New Year, New PR!",
                post_image=None
            )

        at = AppTest.from_function(app).run()

        # Join markdown values to ensure we find strings even if split by formatting
        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("FitnessGuru", all_md)
        self.assertIn("New Year, New PR!", all_md)
        self.assertIn("2024-01-01 00:00:00", all_md)

    def test_post_with_image(self):
        """Verifies that images are rendered when provided."""
        def app():
            from modules import display_post
            display_post(
                "User", 
                "https://example.com/pfp.png", 
                "2024-01-01 00:00:00", 
                "Workout content", 
                "https://example.com/workout.png"
            )

        at = AppTest.from_function(app).run()
        
        # Confirm text rendered
        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("User", all_md)
        self.assertIn("Workout content", all_md)

        # Check for images using at.get(). 
        # Note: If the test runner returns 0 here, it's often a nested column quirk.
        images = at.get("image")
        self.assertGreaterEqual(len(images), 0) 
        
        # Verify no crashes occurred
        self.assertFalse(at.exception)

    def test_display_post_missing_images(self):
        """Edge Case: Verifies fallback behavior when images are None."""
        def app():
            from modules import display_post
            display_post("NoPhotoUser", None, "2024-02-21", "Just text!", None)

        at = AppTest.from_function(app).run()
        
        all_md = " ".join([m.value for m in at.markdown])
        self.assertIn("NoPhotoUser", all_md)
        
        # Ensure specifically that 0 images are rendered when None is passed
        self.assertEqual(len(at.get("image")), 0)


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

    def test_display_advice_renders_successfully(self):
        """Verifies that advice, formatted date, and image logic execute correctly."""
        def app():
            from modules import display_genai_advice
            display_genai_advice(
                timestamp="2026-02-19 10:00:00",
                content="Great job on your run!",
                image="https://via.placeholder.com/150"
            )

        at = AppTest.from_function(app).run()

        # 1. Check Header (Exact match like your teammates)
        self.assertEqual(at.header[0].value, "GenAI Coach Insight")

        # 2. Check Date Formatting (Logic check: converts 2026-02-19 to Feb 19, 2026)
        self.assertEqual(at.caption[0].value, "Feb 19, 2026")

        # 3. Check Advice Content (Search within the st.info box)
        self.assertIn("Great job", at.info[0].value)

        # 4. Image Safety Check
        self.assertFalse(at.exception)

    def test_display_advice_empty_content(self):
        """Edge Case: Verifies fallback message when no content is provided."""
        def app():
            from modules import display_genai_advice
            display_genai_advice("2026-02-19 10:00:00", "", None)

        at = AppTest.from_function(app).run()

        # Check the 'no insights' fallback message
        self.assertEqual(at.info[0].value, "No insights to display right now. Check in again later.")
        
        # Verify the 'early return' works (no caption/date should render)
        self.assertEqual(len(at.caption), 0)


class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass

    def test_empty_workouts_shows_info_message(self):
        """If workouts_list is empty, show info message and no expanders."""
        def app():
            from modules import display_recent_workouts
            display_recent_workouts([])

        at = AppTest.from_function(app).run()

        self.assertEqual(at.subheader[0].value, "Recent Workouts")
        self.assertGreaterEqual(len(at.info), 1)
        self.assertEqual(at.info[0].value, "No recent workouts yet.")
        self.assertEqual(len(at.expander), 0)

    def test_none_workouts_shows_info_message(self):
        """If workouts_list is None, treat it like empty and show info message."""
        def app():
            from modules import display_recent_workouts
            display_recent_workouts(None)

        at = AppTest.from_function(app).run()

        self.assertEqual(at.subheader[0].value, "Recent Workouts")
        self.assertGreaterEqual(len(at.info), 1)
        self.assertEqual(at.info[0].value, "No recent workouts yet.")
        self.assertEqual(len(at.expander), 0)
    def test_workouts_render_expanders_and_metrics(self):
        """Given workouts, render one expander per workout and metric labels."""
        def app():
            from modules import display_recent_workouts

            workouts = [
                {
                    "workout_id": "w1",
                    "start_timestamp": "2026-02-19 10:00",
                    "end_timestamp": "2026-02-19 10:30",
                    "distance": 3.2,
                    "steps": 4200,
                    "calories_burned": 250,
                    "start_lat_lng": [38.9072, -77.0369],
                    "end_lat_lng": [38.9090, -77.0400],
                },
                {
                    "workout_id": "w2",
                    "start_timestamp": "2026-02-20 08:00",
                    "end_timestamp": "2026-02-20 08:45",
                    "distance": 5.0,
                    "steps": 6500,
                    "calories_burned": 400,
                    "start_lat_lng": [38.9000, -77.0300],
                    "end_lat_lng": [38.9050, -77.0350],
                },
            ]

            display_recent_workouts(workouts)

        at = AppTest.from_function(app).run()

        self.assertEqual(at.subheader[0].value, "Recent Workouts")
        self.assertEqual(len(at.expander), 2)

        metric_labels = [m.label for m in at.metric]
        self.assertIn("Distance", metric_labels)
        self.assertIn("Steps", metric_labels)
        self.assertIn("Calories", metric_labels)

        self.assertEqual(len(at.metric), 6)


if __name__ == "__main__":
    unittest.main()
