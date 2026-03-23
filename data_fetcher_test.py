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
from data_fetcher import get_user_workouts

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

if __name__ == "__main__":
    unittest.main()