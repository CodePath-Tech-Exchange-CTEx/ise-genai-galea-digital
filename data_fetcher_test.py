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
from data_fetcher import get_user_sensor_data

class TestDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass

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