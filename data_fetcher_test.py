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
from google.cloud import exceptions
from data_fetcher import get_user_profile, get_user_posts, get_user_sensor_data, get_user_workouts, get_genai_advice

class TestGetUserProfile(unittest.TestCase):
    """Test suite for the get_user_profile function."""
    def setUp(self):
        self.user_id = "user2"
        self.mock_client = MagicMock()

    # FUNCTIONAL REQUIREMENTS

    def test_get_user_profile_success(self):
        """Test that profile data and friends list are correctly mapped."""
        # Setup the mock row
        mock_row = MagicMock()
        mock_row.full_name = 'Bob Smith'
        mock_row.username = 'bobsmith'
        mock_row.date_of_birth = '1985-06-20'
        mock_row.profile_image = 'http://example.com/bob.jpg'
        mock_row.friends = ['user1', 'user3']

        # .query() returns a mock_job
        # .query().result() returns the list of rows
        self.mock_client.query.return_value.result.return_value = [mock_row]

        # Inject the mock_client
        result = get_user_profile(self.user_id, client=self.mock_client)

        # Assertions
        self.assertEqual(result['full_name'], 'Bob Smith')
        self.assertEqual(result['username'], 'bobsmith')
        self.assertIsInstance(result['friends'], list)
        self.assertEqual(len(result['friends']), 2)
        self.assertIn('user1', result['friends'])

    def test_query_parameters_passed(self):
        """Verify the query uses @user_id to prevent SQL injection."""
        # We need a return value so the function doesn't crash before the check
        self.mock_client.query.return_value.result.return_value = [MagicMock()]
        
        get_user_profile(self.user_id, client=self.mock_client)
        
        args, _ = self.mock_client.query.call_args
        query_str = args[0]
    
    # INPUT EDGE CASES

    def test_invalid_input_none(self):
        """Test how the function handles a None user_id."""
        with self.assertRaises(ValueError):
            get_user_profile(None, client=self.mock_client)

    # DATA EDGE CASES

    def test_get_user_profile_not_found(self):
        """Ensure ValueError is raised if BigQuery returns no rows."""
        self.mock_client.query.return_value.result.return_value = [] 

        with self.assertRaises(ValueError):
            get_user_profile("non_existent_user", client=self.mock_client)

    def test_schema_types(self):
        """Verify data types match the UI requirements (dates as strings)."""
        mock_row = MagicMock()
        mock_row.date_of_birth = '1990-01-15' # Already cast to string in SQL
        mock_row.friends = []
        
        self.mock_client.query.return_value.result.return_value = [mock_row]
        
        result = get_user_profile(self.user_id, client=self.mock_client)
        self.assertIsInstance(result['date_of_birth'], str)
    
    # INFRASTRUCTURE & INTEGRATION ERRORS

    def test_bigquery_authentication_error(self):
        """Simulate a 403 Forbidden error."""
        self.mock_client.query.side_effect = exceptions.Forbidden("Access Denied")
        
        with self.assertRaises(exceptions.Forbidden):
            get_user_profile(self.user_id, client=self.mock_client)
    
    def test_bigquery_timeout(self):
        """Simulate a network timeout."""
        self.mock_client.query.side_effect = exceptions.InternalServerError("Timeout")
        
        with self.assertRaises(exceptions.InternalServerError):
            get_user_profile(self.user_id, client=self.mock_client)

class TestGetUserPosts(unittest.TestCase):
    """Test suite for the get_user_posts function."""
    def setUp(self):
        self.user_id = "user1"
        self.mock_client = MagicMock()

        # FUNCTIONAL REQUIREMENTS

    def test_get_user_posts_success(self):
        """Test that posts are correctly mapped from BigQuery rows to list of dicts."""
        # Setup the mock row
        mock_row = MagicMock()
        mock_row.user_id = 'user1'
        mock_row.post_id = 'post123'
        mock_row.timestamp = '2024-07-29 12:00:00'
        mock_row.content = 'Had a great workout!'
        mock_row.image = 'http://example.com/image.jpg'

        # Configure the mock client
        self.mock_client.query.return_value.result.return_value = [mock_row]

        # Inject the mock_client
        result = get_user_posts(self.user_id, client=self.mock_client)

        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user_id'], 'user1')
        self.assertEqual(result[0]['post_id'], 'post123')
        self.assertEqual(result[0]['image'], 'http://example.com/image.jpg')

    def test_query_parameters_passed(self):
        """Verify the query uses parameterized inputs to prevent SQL injection."""
        get_user_posts(self.user_id, client=self.mock_client)
        
        args, kwargs = self.mock_client.query.call_args
        query_str = args[0]
        
        self.assertIn('@user_id', query_str)

    # INPUT EDGE CASES

    def test_invalid_input_none(self):
        """Test how the function handles None inputs."""
        with self.assertRaises(ValueError):
            get_user_posts(None, client=self.mock_client)

    # DATA EDGE CASES

    def test_get_user_posts_null_content(self):
        """Verify that posts with null content return None in Python."""
        mock_row = MagicMock()
        mock_row.content = None # Simulating BigQuery NULL
        
        self.mock_client.query.return_value.result.return_value = [mock_row]
        
        result = get_user_posts(self.user_id, client=self.mock_client)
        self.assertIsNone(result[0]['content'])

    def test_get_user_posts_empty_list(self):
        """Ensure an empty list is returned if the user has no posts."""
        self.mock_client.query.return_value.result.return_value = [] 

        result = get_user_posts("new_user", client=self.mock_client)
        self.assertEqual(result, [])

    # INFRASTRUCTURE & INTEGRATION ERRORS

    def test_bigquery_authentication_error(self):
        """Simulate a 401/403 Forbidden error."""
        self.mock_client.query.side_effect = exceptions.Forbidden("Access Denied")
        
        with self.assertRaises(exceptions.Forbidden):
            get_user_posts(self.user_id, client=self.mock_client)


    def test_bigquery_timeout(self):
        """Simulate a network timeout."""
        self.mock_client.query.side_effect = exceptions.InternalServerError("Timeout")
        
        with self.assertRaises(exceptions.InternalServerError):
            get_user_posts(self.user_id, client=self.mock_client)

class TestGetUserSensorData(unittest.TestCase):

    def setUp(self):
        self.user_id = "user_123"
        self.workout_id = "workout_456"
        
        self.mock_client = MagicMock()

    # FUNCTIONAL REQUIREMENTS

    def test_get_user_sensor_data_success(self):
        """Test that data is correctly mapped from BigQuery rows to list of dicts."""
        mock_row_1 = MagicMock()
        mock_row_1.sensor_type = 'heart_rate'
        mock_row_1.timestamp = '2024-01-01 10:00:00'
        mock_row_1.data = 75.5
        mock_row_1.units = 'bpm'

        self.mock_client.query.return_value.result.return_value = [mock_row_1]

        result = get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['sensor_type'], 'heart_rate')
        self.assertIsInstance(result[0]['data'], float)
        self.assertEqual(result[0]['units'], 'bpm')

    def test_query_parameters_passed(self):
        """Verify the query uses parameterized inputs to prevent SQL injection."""
        get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)
        
        # Check the arguments passed to the .query() method
        args, kwargs = self.mock_client.query.call_args
        query_str = args[0]
        
        self.assertIn('@user_id', query_str)
        self.assertIn('@workout_id', query_str)

    # INPUT EDGE CASES

    def test_invalid_input_none(self):
        """Test how the function handles None inputs (No mock needed for logic check)."""
        with self.assertRaises(ValueError):
            get_user_sensor_data(None, None, client=self.mock_client)

    # DATA EDGE CASES

    def test_no_results_found_user_missing(self):
        """When no results and user doesn't exist, raise ValueError for missing user."""
        self.mock_client.query.return_value.result.return_value = []

        with self.assertRaises(ValueError) as ctx:
            get_user_sensor_data("fake_user", "fake_workout", client=self.mock_client)

        self.assertIn("fake_user", str(ctx.exception))
    
    def test_no_results_found_workout_missing(self):
        """When no results but user exists, raise ValueError for missing workout."""
        self.mock_client.query.return_value.result.side_effect = [
            [],
            [self.mock_client]
        ]

        with self.assertRaises(ValueError) as ctx:
            get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)

        self.assertIn(self.workout_id, str(ctx.exception))
        self.assertIn(self.user_id, str(ctx.exception))
        

    def test_missing_column_in_schema(self):
        """Test resilience if a row is missing an expected attribute."""
        mock_row = MagicMock(spec=[]) # spec=[] ensures it has no attributes
        self.mock_client.query.return_value.result.return_value = [mock_row]

        with self.assertRaises(AttributeError):
            get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)

    # INFRASTRUCTURE & INTEGRATION ERRORS

    def test_bigquery_authentication_error(self):
        """Simulate a 401/403 Forbidden error."""
        self.mock_client.query.side_effect = exceptions.Forbidden("Access Denied")
        
        with self.assertRaises(exceptions.Forbidden):
            get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)

    def test_bigquery_timeout(self):
        """Simulate a network timeout."""
        self.mock_client.query.side_effect = exceptions.InternalServerError("Timeout")
        
        with self.assertRaises(exceptions.InternalServerError):
            get_user_sensor_data(self.user_id, self.workout_id, client=self.mock_client)
            
class TestGetUserWorkouts(unittest.TestCase):
    """Tests for get_user_workouts."""
    def test_foo(self):
        """Tests foo."""
        pass
    
    def test_returns_formatted_workouts(self):
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

        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = fake_rows
        mock_client.query.return_value = mock_query_job

        workouts = get_user_workouts("user1", client=mock_client)

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

    def test_handles_missing_optional_fields(self):
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

        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = fake_rows
        mock_client.query.return_value = mock_query_job

        workouts = get_user_workouts("user2", client=mock_client)

        self.assertEqual(len(workouts), 1)
        self.assertEqual(workouts[0]["workout_id"], "workout2")
        self.assertIsNone(workouts[0]["start_timestamp"])
        self.assertIsNone(workouts[0]["end_timestamp"])
        self.assertIsNone(workouts[0]["start_lat_lng"])
        self.assertIsNone(workouts[0]["end_lat_lng"])
        self.assertIsNone(workouts[0]["distance"])
        self.assertIsNone(workouts[0]["steps"])
        self.assertIsNone(workouts[0]["calories_burned"])

    def test_raises_error_when_no_results(self):
        """Tests that get_user_workouts raises ValueError when no workouts are found."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        with self.assertRaises(ValueError):
            get_user_workouts("unknown_user", client=mock_client)

    def test_builds_query_with_user_id(self):
        """Tests that get_user_workouts sends the expected query and job config."""
        mock_client = MagicMock()
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job

        try:
            get_user_workouts("user123", client=mock_client)
        except ValueError:
            pass  # expected due to empty results

        args, kwargs = mock_client.query.call_args
        self.assertIn("FROM amier-davis-hu.ISE.Workouts", args[0])
        self.assertIn("WHERE UserId = @user_id", args[0])
        self.assertIn("job_config", kwargs)

    def test_raises_value_error_when_user_id_is_none(self):
        """Tests that get_user_workouts raises ValueError when user_id is None."""
        mock_client = MagicMock()

        with self.assertRaises(ValueError):
            get_user_workouts(None, client=mock_client)
            
class TestGetGenaiAdvice(unittest.TestCase):
    """Tests for get_genai_advice."""

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.random")
    def test_returns_formatted_advice(self, mock_random, mock_get_username):
        """Tests that get_genai_advice returns correctly formatted advice data."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.8

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Stay consistent with your workouts."
        mock_model.generate_content.return_value = mock_response

        advice = get_genai_advice("user1", model=mock_model)

        self.assertEqual(advice["content"], "Stay consistent with your workouts.")
        self.assertIsNone(advice["image"])
        self.assertIn("advice_id", advice)
        self.assertIn("timestamp", advice)

        mock_model.generate_content.assert_called_once()

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.random")
    def test_includes_image_when_random_value_is_less_than_half(
        self, mock_random, mock_get_username
    ):
        """Tests that get_genai_advice includes an image when random.random() < 0.5."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.2

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Keep going."
        mock_model.generate_content.return_value = mock_response

        advice = get_genai_advice("user1", model=mock_model)

        self.assertEqual(advice["content"], "Keep going.")
        self.assertIsNotNone(advice["image"])

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.choice")
    @patch("data_fetcher.random.random")
    def test_uses_fallback_advice_when_model_fails(
        self, mock_random, mock_choice, mock_get_username
    ):
        """Tests that get_genai_advice uses fallback advice when model generation fails."""
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.8
        mock_choice.return_value = "Fallback advice"

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")

        advice = get_genai_advice("user1", model=mock_model)

        self.assertEqual(advice["content"], "Fallback advice")
        self.assertIsNone(advice["image"])

if __name__ == "__main__":
    unittest.main()
