import unittest

from flask_dance.consumer.storage import MemoryStorage

from app import create_app
from fixures.spotify import SpotifyAuthentificationTestService
from web.views import HomeView


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        HomeView.service = SpotifyAuthentificationTestService()
        app = create_app()
        storage = MemoryStorage({'access_token': 'fake-token'})
        app.blueprints['spotify'].storage = storage
        self.test_client = app.test_client()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)


if __name__ == '__main__':
    unittest.main()
