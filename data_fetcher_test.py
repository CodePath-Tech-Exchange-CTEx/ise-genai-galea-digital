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
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

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

if __name__ == "__main__":
    unittest.main()