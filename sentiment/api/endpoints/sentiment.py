import logging

from flask import current_app, request
from flask_restx import Resource

from sentiment.api.restplus import api
from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.service import SpotifyAuthenticationService
from sentiment.web.auth import AppContextAttributesMixin

ns = api.namespace('sentiment', description='Sentiment Operations for Spotify')


class UnauthenticatedException(Exception):
    def __init__(self):
        super(UnauthenticatedException, self).__init__('Please provide Bearer Authentication')


@ns.route('/<int:sentiment_id>/playlist')
class SentimentPlaylist(Resource, AppContextAttributesMixin):
    log = logging.getLogger(__name__)

    @property
    def auth_service(self) -> SpotifyAuthenticationService:
        return self._get_or_create_and_store('auth_service', SpotifyAuthenticationService())

    def get(self, sentiment_id):
        auth_header = request.headers.get('Authorization')
        if not (auth_header and auth_header.startswith('Bearer ')):
            raise UnauthenticatedException()

        auth_token = auth_header[len('Bearer '):]
        self.auth_service.configure_token(current_app.config['SECRET_KEY'])
        self.auth_service.catch_authentification_from_auth_token(auth_token)

        return self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(
            Sentiment(sentiment_id))
