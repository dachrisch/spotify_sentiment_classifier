import unittest

from flask_dance.consumer.storage import MemoryStorage

from api.endpoints.sentiment import Analyse
from app import create_app
from fixures.spotify import SpotifyTestConnector
from spotify.service import SpotifyAuthentificationService, SpotifyMoodClassificationService


class SpotifyAuthentificationTestService(SpotifyAuthentificationService):
    def with_token(self, token):
        return SpotifyMoodClassificationService(SpotifyTestConnector())


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        Analyse.service = SpotifyAuthentificationTestService()
        app = create_app()
        storage = MemoryStorage({'access_token': 'fake-token'})
        app.blueprints['spotify'].storage = storage
        self.test_client = app.test_client()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)

    def test_analyse(self):
        response = self.test_client.post('/api/sentiment/analyse', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'"Created"', response.data)


if __name__ == '__main__':
    unittest.main()
