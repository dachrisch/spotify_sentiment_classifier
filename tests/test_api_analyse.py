import unittest

from flask_dance.consumer.storage import MemoryStorage

from app import create_app
from sentiment.api.endpoints.sentiment import Analyse
from tests.fixtures.spotify import SpotifyAuthenticationTestService


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        Analyse.service = SpotifyAuthenticationTestService()
        app = create_app()
        storage = MemoryStorage({'access_token': 'fake-token'})
        app.blueprints['spotify'].storage = storage
        self.test_client = app.test_client()

    def test_analyse(self):
        response = self.test_client.post('/api/sentiment/analyse', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'"Created"', response.data)


if __name__ == '__main__':
    unittest.main()
