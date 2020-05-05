import unittest

from api.endpoints.sentiment import Analyse
from app import create_app
from classify.classify import SpotifyAuthentificationService, SpotifyMoodClassification
from fixures.spotify import SpotifyTestConnector


class SpotifyAuthentificationTestService(SpotifyAuthentificationService):
    def for_user(self, user_id):
        return SpotifyMoodClassification(SpotifyTestConnector())


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        Analyse.service = SpotifyAuthentificationTestService()
        self.app = create_app().test_client()

    def test_homepage(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<a href="/api/sentiment/analyse">Analyze your Spotify Library</a>', response.data)

    def test_analyse(self):
        response = self.app.post('/api/sentiment/analyse', follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'"Created"', response.data)


if __name__ == '__main__':
    unittest.main()
