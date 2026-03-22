#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from data_fetcher import get_user_profile, get_user_posts, get_user_sensor_data, get_user_workouts, get_genai_advice

class TestGetUserProfile(unittest.TestCase):
    def test_get_user_profile_success(self):
        """Tests that a valid user profile is returned correctly."""
        # Using 'user2' (Bob Smith)
        user_id = 'user2'
        profile = get_user_profile(user_id)

        # Check basic info
        self.assertEqual(profile['full_name'], 'Bob Smith')
        self.assertEqual(profile['username'], 'bobsmith')
        self.assertEqual(profile['date_of_birth'], '1985-06-20')
        
        # Check friends
        self.assertIn('user1', profile['friends'])
        self.assertIn('user3', profile['friends'])
        self.assertEqual(len(profile['friends']), 2)

    def test_get_user_profile_friends_bidirectional(self):
        """Verify friends are found regardless of which column the UserID is in."""
        # user2 should have user1 and user3 in their list
        profile = get_user_profile('user2')
        
        self.assertIn('user1', profile['friends'], "Should find user1 from UserId2 column")
        self.assertIn('user3', profile['friends'], "Should find user3 from UserId1 column")
        self.assertEqual(len(profile['friends']), 2)

    def test_get_user_profile_schema_format(self):
        """Verify all dictionary keys exist and data types are correct for the UI."""
        profile = get_user_profile('user1')
        
        # Check that date_of_birth is a string (e.g., '1990-01-15') and not a Python Date object
        self.assertIsInstance(profile['date_of_birth'], str)
        
        # Check that friends is a list of strings, not a list of BigQuery Row objects
        self.assertIsInstance(profile['friends'], list)
        if len(profile['friends']) > 0:
            self.assertIsInstance(profile['friends'][0], str)

    def test_get_user_profile_not_found(self):
        """Tests that a ValueError is raised for a non-existent user."""
        with self.assertRaises(ValueError):
            get_user_profile('non_existent_user_999')

if __name__ == "__main__":
    unittest.main()