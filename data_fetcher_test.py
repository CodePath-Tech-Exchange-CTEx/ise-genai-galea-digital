#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from data_fetcher import get_genai_advice

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