import unittest

from sentiment.api.endpoints.sentiment import Playlist
from sentiment.classify.sentiment import Sentiment
from tests.web_testing_base import TestClientMixin


class TestSentimentAnalyseApi(unittest.TestCase, TestClientMixin):

    def setUp(self):
        self._setup_testclient()
        self._setup_account_as_analysed()
        Playlist._auth_service = self._auth_service

    def test_analyse(self):
        self._auth_service.configure_token(self.test_app.config['SECRET_KEY'])
        self._auth_service.token = {'access_token': 'fake-token', 'expires_in': 1}
        self._auth_service.authorized = True

        response = self.test_client.get('/api/sentiment/playlist',
                                        json={'auth_token': self._auth_service.auth_token,
                                              'sentiment': Sentiment.ANGER.name},
                                        follow_redirects=False)
        self.assertEqual(200, response.status_code, response)
        self.assertIn(b'"name": "gm_mood_2"', response.data)


if __name__ == '__main__':
    unittest.main()
