from urllib.parse import urlparse

import pytest
from betamax import Betamax
from bs4 import BeautifulSoup
from flask import Flask
from flask.testing import FlaskClient
from flask_dance.consumer.storage import MemoryStorage
from flask_dance.contrib.spotify import spotify
from werkzeug.wrappers import Response

from sentiment.web import create_app

with Betamax.configure() as config:
    config.cassette_library_dir = 'fixtures/betamax'


@pytest.fixture
def app():
    test_app = create_app()
    test_app.debug = False
    return test_app


@pytest.fixture
def flask_dance_sessions():
    return spotify


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


class FlaskClientSetup:
    def __init__(self, client: FlaskClient):
        self.client = client

    def on(self, base_url: str):
        self.base_url = base_url
        return self

    def validate_that(self):
        return FlaskClientValidator(self.client, self.base_url)


def with_client(client: FlaskClient):
    return FlaskClientSetup(client)


@pytest.mark.usefixtures("betamax_record_flask_dance")
def test_not_logged_in_from_homepage_to_spotify(app: Flask):
    app.blueprints['spotify'].storage = MemoryStorage({})
    with app.test_client() as client:
        with_client(client).on('https://localhost').validate_that() \
            .get('/').responds(200) \
            .click_button(id='own_music').responds(200).on_page('/player/') \
            .click_button(id='spotify_login').responds(302).on_page('/login/?next=%2Fplayer%2F') \
            .follow_redirect().to('/login/spotify').follow_redirect().to('https://accounts.spotify.com/authorize')
