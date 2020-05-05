import unittest

from flask_dance.consumer.storage import MemoryStorage

from api.endpoints.sentiment import Analyse
from app import create_app
from classify.classify import SpotifyAuthentificationService, SpotifyMoodClassification
from fixures.spotify import SpotifyTestConnector


class SpotifyAuthentificationTestService(SpotifyAuthentificationService):
    def with_token(self, token):
        return SpotifyMoodClassification(SpotifyTestConnector())


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
        self.assertIn(b'<button class="btn-link"> Analyse Library</button>', response.data)

    def test_analyse(self):
        response = self.test_client.post('/api/sentiment/analyse', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'"Created"', response.data)


if __name__ == '__main__':
    unittest.main()
