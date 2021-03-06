import unittest

from sentiment.api.endpoints.sentiment import SentimentPlaylist, UnauthenticatedException
from tests.web_testing_base import TestClientMixin


class TestSentimentApi(unittest.TestCase, TestClientMixin):

    def setUp(self):
        self._setup_testclient()
        self._setup_account_as_analysed()
        SentimentPlaylist._auth_service = self._auth_service

    def test_playlist_from_valid_authentication(self):
        self._auth_service.configure_secret_key(self.test_app.config['SECRET_KEY'])
        self._auth_service.token = {'access_token': 'fake-token', 'expires_in': 1}
        self._auth_service.authorized = True
        auth_token = self._auth_service.auth_token

        self._auth_service.authorized = False
        response = self.test_client.get('/api/sentiment/1/config',
                                        headers=dict(Authorization='Bearer {}'.format(auth_token)),
                                        follow_redirects=False)
        self.assertEqual(200, response.status_code, response)
        self.assertIn(b'''{\n    "classification": {\n        "name": "1"\n    },''', response.data)

    def test_unauthenticated(self):
        with self.assertRaises(UnauthenticatedException):
            response = self.test_client.get('/api/sentiment/TEST/config',
                                            follow_redirects=False)


if __name__ == '__main__':
    unittest.main()
