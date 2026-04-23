import unittest
from datetime import datetime, timedelta
from streamlit.testing.v1 import AppTest


def _make_workout(calories: float, days_ago: int = 0) -> dict:
    ts = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
    return {"calories_burned": calories, "timestamp": ts}

class TestParseDate(unittest.TestCase):
    def setUp(self):
        from calorie_goal import _parse_date
        self.parse = _parse_date

    def test_none_returns_today(self):
        self.assertEqual(self.parse(None), datetime.now().date())

    def test_valid_string(self):
        result = self.parse("2026-03-20 08:00:00")
        self.assertEqual((result.year, result.month, result.day), (2026, 3, 20))

    def test_invalid_string_returns_today(self):
        self.assertEqual(self.parse("not-a-date"), datetime.now().date())


class TestCalorieAggregation(unittest.TestCase):
    def setUp(self):
        from calorie_goal import _get_today_calories, _get_week_calories, _calories_burned
        self.today_cal = _get_today_calories
        self.week_cal = _get_week_calories
        self.burned = _calories_burned

    def test_today_sums_correctly(self):
        workouts = [_make_workout(200), _make_workout(150)]
        self.assertEqual(self.today_cal(workouts), 350)

    def test_today_excludes_past(self):
        self.assertEqual(self.today_cal([_make_workout(500, days_ago=3)]), 0)

    def test_week_excludes_old(self):
        self.assertEqual(self.week_cal([_make_workout(999, days_ago=10)]), 0)

    def test_daily_mode_dispatch(self):
        workouts = [_make_workout(250), _make_workout(500, days_ago=5)]
        self.assertEqual(self.burned(workouts, "Daily"), 250)

    def test_weekly_mode_dispatch(self):
        self.assertGreaterEqual(self.burned([_make_workout(250)], "Weekly"), 250)

class TestDisplayCalorieGoal(unittest.TestCase):

    def test_renders_key_elements(self):
        """Subheader, label, and Edit Goal button all render."""
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([])
        at = AppTest.from_function(app).run()
        self.assertFalse(at.exception)
        self.assertIn("Progress", [e.value for e in at.get("subheader")])
        self.assertIn("Calorie Goal", " ".join(e.value for e in at.get("markdown")))
        self.assertIn("Edit Goal", [b.label for b in at.get("button")])

    def test_daily_caption(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([])
        at = AppTest.from_function(app).run()
        self.assertIn("Today", " ".join(e.value for e in at.get("caption")))

    def test_weekly_caption(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Weekly"
            display_calorie_goal([])
        at = AppTest.from_function(app).run()
        self.assertIn("This Week", " ".join(e.value for e in at.get("caption")))

    def test_goal_crushed_at_100_pct(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            from datetime import datetime
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([{"calories_burned": 500, "timestamp": ts}])
        at = AppTest.from_function(app).run()
        self.assertIn("Goal crushed", " ".join(e.value for e in at.get("success")))

    def test_almost_there_at_80_pct(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            from datetime import datetime
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([{"calories_burned": 400, "timestamp": ts}])
        at = AppTest.from_function(app).run()
        self.assertIn("Almost there", " ".join(e.value for e in at.get("info")))

    def test_remaining_caption_at_20_pct(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            from datetime import datetime
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.calorie_goal_target = 500
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([{"calories_burned": 100, "timestamp": ts}])
        at = AppTest.from_function(app).run()
        self.assertIn("remaining", " ".join(e.value for e in at.get("caption")))

    def test_zero_goal_no_crash(self):
        def app():
            import streamlit as st
            from calorie_goal import display_calorie_goal
            st.session_state.calorie_goal_target = 0
            st.session_state.calorie_goal_type = "Daily"
            display_calorie_goal([])
        at = AppTest.from_function(app).run()
        self.assertFalse(at.exception)

    def test_session_state_defaults(self):
        def app():
            from calorie_goal import display_calorie_goal
            display_calorie_goal([])
        at = AppTest.from_function(app).run()
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()