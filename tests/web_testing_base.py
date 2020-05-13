import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from flask_dance.consumer.storage import MemoryStorage
from requests import Response

from sentiment.classify.sentiment import Sentiment
from sentiment.web import create_app
from sentiment.web.views import HomeView, AnalyseView, MoodPlayerView
from tests.fixtures.spotify import SpotifyAuthenticationTestService


class WithTestClientMixin(object):
    def _setup_testclient(self):
        HomeView.service = SpotifyAuthenticationTestService()
        AnalyseView.service = SpotifyAuthenticationTestService()
        MoodPlayerView.service = SpotifyAuthenticationTestService()
        os.environ['FLASK_CONFIGURATION'] = 'development'
        self.test_app = create_app()
        self.test_client = self.test_app.test_client()

    def _setup_logged_in(self):
        self.storage = MemoryStorage({'access_token': 'fake-token', 'expires_in': 1})
        self.test_app.blueprints['spotify'].storage = self.storage

    def _setup_not_logged_in(self):
        self.test_app.blueprints['spotify'].storage = MemoryStorage()

    def _setup_account_as_analysed(self):
        for sentiment in Sentiment:
            HomeView.service.with_token(None).playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',),
                                                                                      sentiment)
            MoodPlayerView.service.with_token(None).playlist_manager.add_tracks_to_playlist(
                ('2p9RbgJwcuxasdMrQBdDDA3p',),
                sentiment)

    def _setup_token_expired(self):
        self.storage.token['expires_in'] = -1


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


class FlaskClientValidator(object):
    def __init__(self, client: FlaskClient, base_url: str):
        self.base_url = base_url
        self.client = client

    def get(self, url):
        response = self.client.get(url, base_url=self.base_url, follow_redirects=False)
        return ResponseValidator(self, url, response)


def expect_urls_matching(expected: str, actual: str, message: str):
    expected_url = urlparse(expected)
    actual_url = urlparse(actual)
    assert (not expected_url.scheme) or expected_url.scheme == actual_url.scheme, message
    assert (not expected_url.netloc) or expected_url.netloc == actual_url.netloc, message
    assert (not expected_url.path) or expected_url.path == actual_url.path, message
    assert (not expected_url.params) or expected_url.params == actual_url.params, message


class RedirectValidator(object):
    def __init__(self, flask_client_validator: FlaskClientValidator, location: str):
        self.flask_client_validator = flask_client_validator
        if location.startswith(self.flask_client_validator.base_url):
            self.location = location[len(self.flask_client_validator.base_url):]
        else:
            self.location = location

    def to(self, expected_location):
        expect_urls_matching(expected_location, self.location, 'Expected redirection to [{}], but was [{}]'.format(
            expected_location, self.location))
        return self.flask_client_validator.get(self.location)


class ResponseValidator(object):
    def __init__(self, flask_client_validator: FlaskClientValidator, url: str, response: Response):
        self.url = url
        self.flask_client_validator = flask_client_validator
        self.response = response

    def responds(self, status_code: int):
        message = 'While getting [{}], status code was [{}], but expected [{}]'.format(self.url,
                                                                                       self.response.status_code,
                                                                                       status_code)
        assert status_code == self.response.status_code, message
        return self

    def click_button(self, **find_clause):
        soup = BeautifulSoup(self.response.data, features='html.parser')
        found_button = soup.find(**find_clause)
        assert found_button is not None, 'Button [{}] not found in [{}]'.format(find_clause, soup)
        assert 'href' in found_button.attrs, 'Button [{}] has not HREF: {}'.format(find_clause, found_button)
        return self.flask_client_validator.get(found_button.attrs['href'])

    def on_page(self, page):
        assert self.url == page, 'Expected to be on page [{}], but was [{}]'.format(page, self.url)
        return self

    def follow_redirect(self):
        self.responds(302)
        return RedirectValidator(self.flask_client_validator, self.response.location)


class FlaskClientValidatorFactory(object):
    def __init__(self, client, base_url):
        self.base_url = base_url
        self.client = client

    def validate_that(self):
        return FlaskClientValidator(self.client, self.base_url)


class FlaskClientSetup(object):
    def __init__(self, client: FlaskClient):
        self.client = client

    def on(self, base_url: str):
        return FlaskClientValidatorFactory(self.client, base_url)


def with_client(app: Flask):
    return FlaskClientSetup(app.test_client())
