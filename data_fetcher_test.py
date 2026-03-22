#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

class TestGetUserPosts(unittest.TestCase):
    """Test suite for the get_user_posts function."""

    def test_get_user_posts_success(self):
        """Verify that posts are fetched with the correct keys and values."""
        # Testing user1 (Alice)
        user_id = 'user1'
        posts = get_user_posts(user_id)

        self.assertIsInstance(posts, list)
        self.assertGreater(len(posts), 0)

        # Check the first post's structure
        post = posts[0]
        self.assertEqual(post['user_id'], user_id)
        self.assertIn('post_id', post)
        self.assertIn('content', post)
        self.assertIn('timestamp', post)
        
        # Verify the aliasing: 'ImageUrl' in BigQuery should be 'image' in Python
        self.assertTrue(post['image'].startswith('http'))

    def test_get_user_posts_null_content(self):
        """Verify that posts with null content return None in Python."""
        # Your screenshot showed 'user1' has a null Content field
        posts = get_user_posts('user1')
        post = posts[0]
        
        # BigQuery NULLs become Python None
        self.assertIsNone(post['content'], "Content should be None if it is null in the database")

    def test_get_user_posts_empty_for_new_user(self):
        """Verify that a user with no posts returns an empty list (not an error)."""
        # Assuming 'fake_user' exists in Users but has 0 rows in the Posts table
        posts = get_user_posts('non_existent_user')
        self.assertEqual(posts, [])

if __name__ == "__main__":
    unittest.main()