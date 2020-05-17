import logging

from bunch import Bunch
from flask import current_app
from flask_restx import Resource

from sentiment.api.restplus import api
from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.service import SpotifyAuthenticationService
from sentiment.web.views import AppContextAttributesMixin

ns = api.namespace('sentiment', description='Sentiment Operations for Spotify')

upload_parser = api.parser()
upload_parser.add_argument('auth_token', required=True)
upload_parser.add_argument('sentiment', required=True)


@ns.route('/playlist')
@ns.expect(upload_parser)
class Playlist(Resource, AppContextAttributesMixin):
    log = logging.getLogger(__name__)

    @property
    def auth_service(self) -> SpotifyAuthenticationService:
        return self._get_or_create_and_store('auth_service', SpotifyAuthenticationService())

    def get(self):
        args = Bunch(upload_parser.parse_args())
        self.auth_service.configure_token(current_app.config['SECRET_KEY'])
        self.auth_service.catch_authentification_from_auth_token(args.auth_token)

        return self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(
            Sentiment(int(args.sentiment)))
