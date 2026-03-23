#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
import sys, types
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from data_fetcher import get_genai_advice, get_username

class TestDataFetcher(unittest.TestCase):

    def test_foo(self):
        """Tests foo."""
        pass

    @patch("data_fetcher.get_username")
    @patch("data_fetcher.random.random")
    def test_get_genai_advice_uses_vertex_response(self, mock_random, mock_get_username):
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


    @patch("data_fetcher.st.warning")
    @patch("data_fetcher.random.choice")
    @patch("data_fetcher.random.random")
    @patch("data_fetcher.get_username")
    def test_get_genai_advice_falls_back_when_vertex_fails(
        self, mock_get_username, mock_random, mock_choice, mock_warning
    ):
        mock_get_username.return_value = "Lena"
        mock_random.return_value = 0.8
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

        self.assertIsNotNone(advice["image"])


    @patch("data_fetcher.bigquery.Client")
    def test_get_username_returns_username_from_bigquery(self, mock_client_class):
        fake_client = MagicMock()
        mock_client_class.return_value = fake_client

        fake_query_job = MagicMock()
        fake_query_job.result.return_value = [SimpleNamespace(Username="Lena")]
        fake_client.query.return_value = fake_query_job

        username = get_username("user1")

        self.assertEqual(username, "Lena")


    @patch("data_fetcher.bigquery.Client")
    def test_get_username_returns_default_user_when_not_found(self, mock_client_class):
        fake_client = MagicMock()
        mock_client_class.return_value = fake_client

        fake_query_job = MagicMock()
        fake_query_job.result.return_value = []
        fake_client.query.return_value = fake_query_job

        username = get_username("missing_user")

        self.assertEqual(username, "User")

if __name__ == "__main__":
    unittest.main()