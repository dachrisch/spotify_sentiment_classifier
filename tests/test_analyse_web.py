import unittest
from unittest.mock import MagicMock

from flask_dance.consumer.storage import MemoryStorage

from app import create_app
from fixures.spotify import SpotifyAuthenticationTestService
from web.views import HomeView, AnalyseView, MoodPlayerView


class WasAnalysedCatcher(object):
    def __init__(self):
        self._analyse_was_analysed = False

    # noinspection PyUnusedLocal
    def with_token(self, token):
        return self

    def analyse(self):
        self._analyse_was_analysed = True
        return True

    def analyse_was_called(self):
        return self._analyse_was_analysed


class WithTestClientMixin(object):
    def _setup_testclient(self):
        HomeView.service = SpotifyAuthenticationTestService()
        AnalyseView.service = SpotifyAuthenticationTestService()
        MoodPlayerView.service = SpotifyAuthenticationTestService()
        app = create_app()
        self.storage = MemoryStorage({'access_token': 'fake-token', 'expires_in': 1})
        app.blueprints['spotify'].storage = self.storage
        self.test_client = app.test_client()


class TestAnalyseWeb(unittest.TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_press_analyse_music_button(self):
        AnalyseView.service = WasAnalysedCatcher()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertTrue(AnalyseView.service.analyse_was_called())
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/">', response.data)

    def test_user_has_no_saved_tracks(self):
        AnalyseView.service.connector = MagicMock()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        AnalyseView.service.connector.audio_features.assert_not_called()
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/?error=Analyse+failed%21+You+don%27t+have+any+saved+tracks.">', response.data)



if __name__ == '__main__':
    unittest.main()
