#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import MagicMock
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

if __name__ == "__main__":
    unittest.main()
