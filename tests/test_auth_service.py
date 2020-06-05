import unittest

from sentiment.spotify.service import SpotifyAuthenticationService, TokenNotValidException


class SpotifyFixture(object):
    authorized = True
    token = {'access_token': 'test', 'expires_in': 1}


class TestSpotifyAuthenticationService(unittest.TestCase):

    def test_no_auth_raises_exception(self):
        with self.assertRaises(TokenNotValidException):
            SpotifyAuthenticationService().service_instance

    def test_auth_from_web(self):
        service = SpotifyAuthenticationService()
        service.catch_authentication_from_web(SpotifyFixture())
        self.assertIsNotNone(service.service_instance)

    def test_auth_from_token(self):
        token = self.generate_test_token()
        service = SpotifyAuthenticationService()
        service.configure_secret_key('123')
        service.catch_authentication_from_auth_token(token)
        self.assertIsNotNone(service.service_instance)

    def generate_test_token(self):
        service = SpotifyAuthenticationService()
        service.configure_secret_key('123')
        service.token = SpotifyFixture().token
        service.authorized = True
        token = service.auth_token
        self.assertIsNotNone(token)
        return token
