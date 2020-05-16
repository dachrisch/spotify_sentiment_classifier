import unittest
from unittest.mock import MagicMock

from sentiment.web.views import AnalyseView
from tests.web_testing_base import TestClientMixin, WasAnalysedCatcher


class TestAnalyseWeb(unittest.TestCase, TestClientMixin):

    def setUp(self):
        self._setup_testclient()
        self._setup_logged_in()

    def test_press_analyse_music_button(self):
        AnalyseView.service = WasAnalysedCatcher()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertTrue(AnalyseView.service.analyse_was_called())
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/player/">', response.data)

    def test_user_has_no_saved_tracks(self):
        AnalyseView.service.connector = MagicMock()
        response = self.test_client.post('/analyse/', follow_redirects=False)
        with self.test_client.session_transaction() as session:
            self.assertIn(('error', "Analyse failed! You don't have any saved tracks."), session['_flashes'])
        AnalyseView.service.connector.audio_features.assert_not_called()
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/player/">', response.data)


if __name__ == '__main__':
    unittest.main()
