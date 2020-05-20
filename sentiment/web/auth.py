from typing import Callable

from flask import g, current_app
from flask_dance.contrib.spotify import spotify

from sentiment.spotify.service import SpotifyAuthenticationService


class BeforeRequestDispatcherMixin(object):
    def __init__(self):
        self._before_request_funcs: list[Callable[[str], None]] = []

    def before_request(self, name):
        for before_request_func in self._before_request_funcs:
            before_request_func(name)


class AppContextAttributesMixin(object):
    def _get_or_create_and_store(self, property, default):
        if property not in g:
            setattr(g, property, default)
        return getattr(g, property)


class SpotifyServiceMixin(AppContextAttributesMixin, BeforeRequestDispatcherMixin):
    def __init__(self):
        super().__init__()
        self._before_request_funcs.append(self._catch_auth)

    def _catch_auth(self, name):
        self.auth_service.configure_token(current_app.config.get('SECRET_KEY'))
        self.auth_service.catch_authentication_from_web(spotify)

    def _valid_login(self):
        return self.auth_service.is_token_valid()

    @property
    def auth_service(self) -> SpotifyAuthenticationService:
        return self._get_or_create_and_store('auth_service', SpotifyAuthenticationService())
