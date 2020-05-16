import os
from abc import abstractmethod
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from flask import g
from flask.testing import FlaskClient
from flask_dance.consumer.storage import MemoryStorage
from requests import Response

from sentiment.classify.sentiment import Sentiment
from sentiment.web import create_app
from tests.fixtures.spotify import SpotifyAuthenticationTestService


class TestClientMixin(object):
    def _setup_testclient(self):
        os.environ['FLASK_CONFIGURATION'] = 'development'
        self.test_app = create_app()
        self.test_client = self.test_app.test_client()
        self.test_app.app_context().push()
        self._auth_service = SpotifyAuthenticationTestService()
        g.auth_service = self._auth_service

    def _setup_logged_in(self):
        self.storage = MemoryStorage({'access_token': 'fake-token', 'expires_in': 1})
        self.test_app.blueprints['spotify'].storage = self.storage

    def _setup_not_logged_in(self):
        self.test_app.blueprints['spotify'].storage = MemoryStorage()

    def _setup_account_as_analysed(self):
        for sentiment in Sentiment:
            self._auth_service.service_instance.playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',),
                                                                                        sentiment)

    def _setup_token_expired(self):
        self.storage.token['expires_in'] = -1

    def _run_flow(self):
        return FlaskClientSetup(self.test_app.test_client())


class WasAnalysedCatcher(object):
    def __init__(self):
        self._analyse_was_analysed = False

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

    def post(self, url, **post_data):
        response = self.client.post(url, base_url=self.base_url, follow_redirects=False, **post_data)
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


class ItemValidator(object):
    @classmethod
    def noop(cls):
        return NoopItemValidator()

    @classmethod
    def attr(cls, name, value):
        return ItemAttributeValidator(name, value)

    @abstractmethod
    def validate(self, item_find_clause, item):
        raise NotImplementedError


class ItemAttributeValidator(ItemValidator):

    def __init__(self, name, value):
        self.value = value
        self.name = name

    def validate(self, item_find_clause, item):
        assert self.name in item.attrs, 'Attribute [{}] not found in [{}]'.format(self.name, item.attrs)
        assert self.value == item.attrs[
            self.name], 'Expected item [{}] with attribute [{}] to be [{}], but was [{}]'.format(item_find_clause,
                                                                                                 self.name,
                                                                                                 self.value,
                                                                                                 item.attrs[self.name])


class NoopItemValidator(ItemValidator):
    def validate(self, item_find_clause, item):
        pass


class ResponseValidator(object):
    def __init__(self, flask_client_validator: FlaskClientValidator, url: str, response: Response):
        self.url = url
        self.flask_client_validator = flask_client_validator
        self.response = response

    def responds(self, status_code: int):
        message = 'Status code was [{}], but expected [{}] while getting [{}]: {}'.format(self.response.status_code,
                                                                                          status_code, self.url,
                                                                                          self.response.data)
        assert status_code == self.response.status_code, message
        return self

    def click_button(self, **button_find_clause):
        found_button = self._assert_find(**button_find_clause)
        assert 'href' in found_button.attrs, 'Button [{}] has not HREF: {}'.format(button_find_clause, found_button)
        return self.flask_client_validator.get(found_button.attrs['href'])

    def submit_button(self, in_form, **button_find_clause):
        submit_form = self._assert_find(id=in_form)
        submit_button = self._assert_find(**button_find_clause)
        button_in_form = False
        for parent in submit_button.parents:
            if 'id' in parent.attrs and parent.attrs['id'] == in_form:
                button_in_form = True
                break
        assert button_in_form, 'Button [{}] not found in [{}]'.format(button_find_clause, in_form)
        if not submit_form['method'] == 'post':
            raise Exception('Unknown form method in [{}]'.format(submit_form))

        data = {submit_button['id']: submit_button['id']}
        token = self._find(id='csrf_token')[0]
        if token:
            data['csrf_token'] = token.attrs['value']
        return self.flask_client_validator.post(urlparse(submit_form['action']).path, data=data)

    def on_page(self, page):
        assert self.url == page, 'Expected to be on page [{}], but was [{}]'.format(page, self.url)
        return self

    def has(self, validator=ItemValidator.noop(), **item_find_clause):
        item = self._assert_find(**item_find_clause)
        validator.validate(item_find_clause, item)
        return self

    def _assert_find(self, **item_find_clause):
        item, soup = self._find(**item_find_clause)
        assert item, 'Item [{}] not found in [{}]'.format(item_find_clause, soup)
        return item

    def _find(self, **item_find_clause):
        soup = BeautifulSoup(self.response.data, features='html.parser')
        item = soup.find(**item_find_clause)
        return item, soup

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
