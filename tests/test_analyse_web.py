import unittest

from bs4 import BeautifulSoup
from flask_dance.consumer.storage import MemoryStorage

from app import create_app
from classify.sentiment import Sentiment
from fixures.spotify import SpotifyAuthentificationTestService
from web.views import HomeView


class TestSentimentAnalyseApi(unittest.TestCase):

    def setUp(self):
        HomeView.service = SpotifyAuthentificationTestService()
        app = create_app()
        self.storage = MemoryStorage({'access_token': 'fake-token', 'expires_in': 1})
        app.blueprints['spotify'].storage = self.storage
        self.test_client = app.test_client()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)

    def test_token_expired(self):
        self.storage.token['expires_in'] = -1

        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/login/spotify">', response.data)

    def test_button_active_when_not_analysed(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        button = soup.find(id='btn_analyse')
        self.assertIsNotNone(button)
        self.assertIn('Analyse your music library', button.next)

    def test_button_deactivated_when_analysed(self):
        for sentiment in Sentiment:
            HomeView.service.with_token(None).playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',),
                                                                                      sentiment)

        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.soup = BeautifulSoup(response.data, features='html.parser')
        soup = self.soup
        button = soup.find(id='btn_analysed')
        self.assertIsNotNone(button)
        self.assertIn('Music library analysed', button.next)


if __name__ == '__main__':
    unittest.main()
