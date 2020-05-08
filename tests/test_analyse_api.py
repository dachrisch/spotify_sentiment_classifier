import unittest

from flask_dance.consumer.storage import MemoryStorage

from api.endpoints.sentiment import Analyse
from app import create_app
from fixures.spotify import SpotifyAuthentificationTestService


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        Analyse.service = SpotifyAuthentificationTestService()
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
