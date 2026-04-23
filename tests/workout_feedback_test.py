#############################################################################
# workout_feedback_test.py
#
# This file contains tests for workout_feedback.py.
#############################################################################

import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class TestWorkoutFeedback(unittest.TestCase):

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
            },
            {
                "workout_id": "workout1",
                "start_timestamp": "2024-01-02 00:00:00",
                "end_timestamp": "2024-01-02 00:40:00",
                "start_lat_lng": [2.5, 5.5],
                "end_lat_lng": [2.6, 5.6],
                "distance": 4.2,
                "steps": 8200,
                "calories_burned": 12,
            },
        ]

    def test_initialize_feedback_state_creates_defaults(self):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state

            initialize_feedback_state()

            st.write(st.session_state["workout_feedback"])
            st.write(st.session_state["show_feedback_form"])
            st.write(st.session_state["feedback_css_loaded"])

        at = AppTest.from_function(app).run()

        self.assertEqual(at.session_state["workout_feedback"], {})
        self.assertFalse(at.session_state["show_feedback_form"])
        self.assertFalse(at.session_state["feedback_css_loaded"])

    def test_get_feedback_button_label_returns_add_feedback_when_no_feedback(self):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, get_feedback_button_label

            initialize_feedback_state()
            label = get_feedback_button_label(st.secrets["mock_workouts"])
            st.markdown(label)

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()

        all_markdown = [m.value for m in at.markdown]
        self.assertIn("Add Feedback", all_markdown)

    def test_get_feedback_button_label_returns_edit_feedback_when_feedback_exists(self):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, get_feedback_button_label

            initialize_feedback_state()
            st.session_state["workout_feedback"] = {
                "workout0": {"effort": 5, "motivation": "🙂", "notes": "Good"}
            }

            label = get_feedback_button_label(st.secrets["mock_workouts"])
            st.markdown(label)

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()

        all_markdown = [m.value for m in at.markdown]
        self.assertIn("Edit Feedback", all_markdown)

    def test_load_feedback_css_marks_css_loaded(self):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, load_feedback_css

            initialize_feedback_state()
            load_feedback_css()
            st.write(st.session_state["feedback_css_loaded"])

        at = AppTest.from_function(app).run()
        self.assertTrue(at.session_state["feedback_css_loaded"])

    def test_render_feedback_form_shows_expected_fields(self):
        def app():
            from workout_feedback import initialize_feedback_state, render_feedback_form

            initialize_feedback_state()
            render_feedback_form([
                {
                    "workout_id": "workout0",
                    "start_timestamp": "2024-01-01 00:00:00",
                    "end_timestamp": "2024-01-01 00:30:00",
                }
            ])

        at = AppTest.from_function(app).run()

        subheaders = [s.value for s in at.subheader]
        self.assertIn("Feedback Form", subheaders)

        radio_labels = [r.label for r in at.radio]
        self.assertIn("Select the workout you want to give feedback for:", radio_labels)
        self.assertIn("Choose one", radio_labels)

        text_area_labels = [t.label for t in at.text_area]
        self.assertIn("Notes", text_area_labels)

    @patch("workout_feedback.st.rerun")
    def test_submit_feedback_without_effort_shows_warning(self, mock_rerun):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, render_feedback_form

            initialize_feedback_state()
            render_feedback_form(st.secrets["mock_workouts"])

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()

        submit_button = next(
            b for b in at.button if b.label == "Submit Feedback"
        )
        submit_button.click().run()

        warnings = [w.value for w in at.warning]
        self.assertIn("Please select an effort level.", warnings)
        mock_rerun.assert_not_called()

    @patch("workout_feedback.st.rerun")
    def test_submit_feedback_saves_to_session_state(self, mock_rerun):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, render_feedback_form

            initialize_feedback_state()
            render_feedback_form(st.secrets["mock_workouts"])

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()

        workout_radio = next(
            r for r in at.radio
            if r.label == "Select the workout you want to give feedback for:"
        )
        workout_radio.set_value("Workout 1").run()

        at.session_state["effort_pills_workout0"] = 5
        at.run()

        motivation_radio = next(
            r for r in at.radio
            if r.label == "Choose one"
        )
        motivation_radio.set_value("😁").run()

        notes_area = next(t for t in at.text_area if t.label == "Notes")
        notes_area.set_value("Strong workout").run()

        submit_button = next(
            b for b in at.button if b.label == "Submit Feedback"
        )
        submit_button.click().run()

        saved_feedback = at.session_state["workout_feedback"]["workout0"]
        self.assertEqual(saved_feedback["effort"], 5)
        self.assertEqual(saved_feedback["motivation"], "😁")
        self.assertEqual(saved_feedback["notes"], "Strong workout")
        self.assertFalse(at.session_state["show_feedback_form"])
        mock_rerun.assert_called()

    @patch("workout_feedback.st.rerun")
    def test_cancel_hides_form_and_reruns(self, mock_rerun):
        def app():
            import streamlit as st
            from workout_feedback import initialize_feedback_state, render_feedback_form

            initialize_feedback_state()
            st.session_state["show_feedback_form"] = True
            render_feedback_form(st.secrets["mock_workouts"])

        at = AppTest.from_function(app)
        at.secrets["mock_workouts"] = self.mock_workouts
        at.run()

        cancel_button = next(
            b for b in at.button if b.label == "Cancel"
        )
        cancel_button.click().run()

        self.assertFalse(at.session_state["show_feedback_form"])
        mock_rerun.assert_called()