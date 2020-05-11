import unittest
from unittest.mock import MagicMock

from tests.web_testing_base import WithTestClientMixin, WasAnalysedCatcher
from web.views import AnalyseView


class TestAnalyseWeb(unittest.TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_token_expired(self):
        self.storage.token['expires_in'] = -1

        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/login/spotify">', response.data)

    def test_press_analyse_music_button(self):
        AnalyseView.service = WasAnalysedCatcher()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertTrue(AnalyseView.service.analyse_was_called())
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/player/">', response.data)

    def test_user_has_no_saved_tracks(self):
        AnalyseView.service.connector = MagicMock()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        AnalyseView.service.connector.audio_features.assert_not_called()
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/player/?error=Analyse+failed%21+You+don%27t+have+any+saved+tracks.">', response.data)


if __name__ == '__main__':
    unittest.main()
