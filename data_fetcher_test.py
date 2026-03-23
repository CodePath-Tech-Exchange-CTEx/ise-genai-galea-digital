#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
import sys
import types
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from data_fetcher import get_user_workouts, get_genai_advice, get_username

class TestDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass

    @patch("data_fetcher.client")
    def test_get_user_workouts_returns_formatted_workouts(self, mock_client):
        """Tests that get_user_workouts returns correctly formatted workout data."""

        fake_rows = [
            SimpleNamespace(
                WorkoutId="workout1",
                StartTimestamp=datetime(2024, 1, 1, 8, 0, 0),
                EndTimestamp=datetime(2024, 1, 1, 8, 30, 0),
                StartLocationLat=38.9072,
                StartLocationLong=-77.0369,
                EndLocationLat=38.9090,
                EndLocationLong=-77.0400,
                TotalDistance=3.1,
                TotalSteps=5200,
                CaloriesBurned=245.5,
            )
        ]

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = fake_rows
        mock_client.query.return_value = mock_query_job

        workouts = get_user_workouts("user1")

        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0]["workout_id"], "workout1")
        self.assertEqual(workouts[0]["start_timestamp"], "2024-01-01 08:00:00")
        self.assertEqual(workouts[0]["end_timestamp"], "2024-01-01 08:30:00")
        self.assertEqual(workouts[0]["start_lat_lng"], (38.9072, -77.0369))
        self.assertEqual(workouts[0]["end_lat_lng"], (38.9090, -77.0400))
        self.assertEqual(workouts[0]["distance"], 3.1)
        self.assertEqual(workouts[0]["steps"], 5200)
        self.assertEqual(workouts[0]["calories_burned"], 245.5)

        mock_client.query.assert_called_once()

    @patch("data_fetcher.client")
    def test_get_user_workouts_handles_missing_optional_fields(self, mock_client):
        """Tests that get_user_workouts handles missing values correctly."""

        fake_rows = [
            SimpleNamespace(
                WorkoutId="workout2",
                StartTimestamp=None,
                EndTimestamp=None,
                StartLocationLat=None,
                StartLocationLong=None,
                EndLocationLat=None,
                EndLocationLong=None,
                TotalDistance=None,
                TotalSteps=None,
                CaloriesBurned=None,
            )
        ]

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = fake_rows
        mock_client.query.return_value = mock_query_job

        workouts = get_user_workouts("user2")

        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0]["workout_id"], "workout2")
        self.assertIsNone(workouts[0]["start_timestamp"])
        self.assertIsNone(workouts[0]["end_timestamp"])
        self.assertIsNone(workouts[0]["start_lat_lng"])
        self.assertIsNone(workouts[0]["end_lat_lng"])
        self.assertIsNone(workouts[0]["distance"])
        self.assertIsNone(workouts[0]["steps"])
        self.assertIsNone(workouts[0]["calories_burned"])

    @patch("data_fetcher.client")
    def test_get_user_workouts_returns_empty_list_when_no_results(self, mock_client):
        """Tests that get_user_workouts returns an empty list when no workouts are found."""

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        workouts = get_user_workouts("unknown_user")

        self.assertEqual(workouts, [])

    @patch("data_fetcher.client")
    def test_get_user_workouts_builds_query_with_user_id(self, mock_client):
        """Tests that get_user_workouts sends the query to BigQuery."""

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        get_user_workouts("user123")

        args, kwargs = mock_client.query.call_args
        self.assertIn("FROM amier-davis-hu.ISE.Workouts", args[0])
        self.assertIn("WHERE UserId = @user_id", args[0])
        self.assertIn("job_config", kwargs)

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.random")
    def test_get_genai_advice_uses_vertex_response(self, mock_random, mock_get_username):
        """Tests that get_genai_advice returns Vertex AI content when the API call succeeds."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.8  # no image

        fake_response = SimpleNamespace(text="Keep up the momentum this week!")
        fake_model_instance = MagicMock()
        fake_model_instance.generate_content.return_value = fake_response

        fake_vertexai = types.ModuleType("vertexai")
        fake_vertexai.init = MagicMock()

        fake_generative_models = types.ModuleType("vertexai.generative_models")
        fake_generative_models.GenerativeModel = MagicMock(return_value=fake_model_instance)

        with patch.dict(sys.modules, {
            "vertexai": fake_vertexai,
            "vertexai.generative_models": fake_generative_models,
        }):
            advice = get_genai_advice("user1")

        self.assertTrue(advice["advice_id"].startswith("advice_user1_"))
        self.assertIsInstance(advice["timestamp"], str)
        self.assertEqual(advice["content"], "Keep up the momentum this week!")
        self.assertIsNone(advice["image"])

        fake_vertexai.init.assert_called_once_with(
            project="lena-diouf-hu",
            location="us-central1"
        )
        fake_generative_models.GenerativeModel.assert_called_once_with("gemini-2.5-flash")
        fake_model_instance.generate_content.assert_called_once()

    @patch("data_fetcher.st.warning")
    @patch("data_fetcher.random.choice")
    @patch("data_fetcher.random.random")
    @patch("data_fetcher.get_username")
    def test_get_genai_advice_falls_back_when_vertex_fails(
        self, mock_get_username, mock_random, mock_choice, mock_warning
    ):
        """Tests that get_genai_advice uses fallback advice if Vertex AI raises an exception."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.8  # no image
        mock_choice.return_value = "Fallback advice"

        fake_vertexai = types.ModuleType("vertexai")
        fake_vertexai.init = MagicMock()

        fake_generative_models = types.ModuleType("vertexai.generative_models")

        class FakeGenerativeModel:
            def __init__(self, model_name):
                pass

            def generate_content(self, prompt):
                raise Exception("API failed")

        fake_generative_models.GenerativeModel = FakeGenerativeModel

        with patch.dict(sys.modules, {
            "vertexai": fake_vertexai,
            "vertexai.generative_models": fake_generative_models,
        }):
            advice = get_genai_advice("user1")

        self.assertEqual(advice["content"], "Fallback advice")
        self.assertIsNone(advice["image"])
        mock_warning.assert_called_once()

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.random")
    def test_get_genai_advice_adds_image_sometimes(self, mock_random, mock_get_username):
        """Tests that get_genai_advice includes an image when random.random() < 0.5."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.2  # image included

        fake_response = SimpleNamespace(text="Stay consistent and trust the process.")
        fake_model_instance = MagicMock()
        fake_model_instance.generate_content.return_value = fake_response

        fake_vertexai = types.ModuleType("vertexai")
        fake_vertexai.init = MagicMock()

        fake_generative_models = types.ModuleType("vertexai.generative_models")
        fake_generative_models.GenerativeModel = MagicMock(return_value=fake_model_instance)

        with patch.dict(sys.modules, {
            "vertexai": fake_vertexai,
            "vertexai.generative_models": fake_generative_models,
        }):
            advice = get_genai_advice("user1")

        self.assertEqual(
            advice["image"],
            "https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop"
        )

    @patch("data_fetcher.bigquery.Client")
    def test_get_username_returns_username_from_bigquery(self, mock_client_class):
        """Tests that get_username returns the Username value from the Users table."""
        fake_client = MagicMock()
        mock_client_class.return_value = fake_client

        fake_query_job = MagicMock()
        fake_query_job.result.return_value = [SimpleNamespace(Username="Lena")]
        fake_client.query.return_value = fake_query_job

        username = get_username("user1")

        self.assertEqual(username, "Lena")
        mock_client_class.assert_called_once_with(project="lena-diouf-hu")
        fake_client.query.assert_called_once()

    @patch("data_fetcher.bigquery.Client")
    def test_get_username_returns_default_user_when_not_found(self, mock_client_class):
        """Tests that get_username returns 'User' when no matching row is found."""
        fake_client = MagicMock()
        mock_client_class.return_value = fake_client

        fake_query_job = MagicMock()
        fake_query_job.result.return_value = []
        fake_client.query.return_value = fake_query_job

        username = get_username("missing_user")

        self.assertEqual(username, "User")

if __name__ == "__main__":
    unittest.main()