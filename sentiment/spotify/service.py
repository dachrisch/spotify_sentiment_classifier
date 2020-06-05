import datetime
import logging

import jwt
from flask_dance.contrib.spotify import spotify

from sentiment.classify.classify import FeatureClassifier, Classification
from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.connector import SpotipyConnectionWrapper
from sentiment.spotify.playlist import PlaylistManager


class TokenNotValidException(Exception):
    def __init__(self, token: dict):
        super(TokenNotValidException, self).__init__('Token [{}] not valid'.format(token))


class UserHasNoTracksException(Exception):
    pass


class SpotifyMoodClassificationService(object):
    def __init__(self, spotify_connector: SpotipyConnectionWrapper):
        self.spotify_connector = spotify_connector
        self.playlist_manager = PlaylistManager(self.spotify_connector)
        self.log = logging.getLogger(__name__)

    def analyse(self):
        all_tracks = self._all_tracks()
        if not all_tracks:
            raise UserHasNoTracksException()
        self.log.info('analyzing [%s] tracks for sentiment...' % (len(self._only_ids(all_tracks))))
        all_tracks_features = self._all_tracks_audio_features(all_tracks)

        for sentiment in Sentiment:
            tracks_features_in_sentiment = self._filter_sentiment(sentiment, all_tracks_features)
            track_ids_in_sentiment = self._only_ids(tracks_features_in_sentiment)
            self.log.info('tracks found for [%s]: %d' % (sentiment.name, len(tracks_features_in_sentiment)))
            self.log.debug(list(map(lambda y: {'id': y['id'], 'name': y['name']},
                                    filter(lambda x: x['id'] in track_ids_in_sentiment, all_tracks))))
            self.playlist_manager.add_tracks_to_playlist(track_ids_in_sentiment, sentiment)

    def is_analysed(self):
        return 5 == len(
            list(filter(lambda sentiment: len(self.playlist_manager.tracks_in_playlist(sentiment)) > 0, Sentiment)))

    def username(self):
        return self.spotify_connector.current_user()['display_name']

    def _filter_sentiment(self, sentiment, tracks_with_features):
        return tuple(
            filter(lambda x: FeatureClassifier().classify(x) == Classification(sentiment), tracks_with_features))

    def _all_tracks_audio_features(self, all_tracks):
        all_tracks_features = self.spotify_connector.audio_features(self._only_ids(all_tracks))
        return all_tracks_features

    def _only_ids(self, tracks):
        return tuple(map(lambda x: x['id'], tracks))

    def _all_tracks(self):
        user_saved_tracks = self.spotify_connector.current_user_saved_tracks()
        self.log.debug('user has the following saved tracks: [{}]'.format(user_saved_tracks))
        return tuple(map(lambda x: x['track'], user_saved_tracks['items']))


class SpotifyAuthenticationService(object):
    def __init__(self):
        self.authorized = False
        self.token = {}
        self.secret_key = None

    @property
    def service_instance(self) -> SpotifyMoodClassificationService:
        if not self.is_token_valid():
            raise TokenNotValidException(self.token)
        return SpotifyMoodClassificationService(SpotipyConnectionWrapper.from_token(self.token['access_token']))

    def catch_authentication_from_web(self, spotify_authentication: spotify):
        self.authorized = spotify_authentication.authorized
        self.token = spotify_authentication.token

    def catch_authentification_from_auth_token(self, auth_token):
        if not self.secret_key:
            raise Exception('Secret key not configured. Have you called [{}]?'.format(self.configure_token))
        payload = jwt.decode(auth_token, self.secret_key, algorithms=('HS256',))
        if payload and 'sub' in payload:
            self.token = payload['sub']

    def is_token_valid(self):
        if self.token and 'expires_in' in self.token:
            return self.authorized and (self.token['expires_in'] > 0)
        else:
            return self.authorized

    @property
    def auth_token(self):
        if not self.secret_key:
            raise Exception('Secret key not configured. Have you called [{}]?'.format(self.configure_token))
        auth_token = None
        if self.is_token_valid():
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                'iat': datetime.datetime.utcnow(),
                'sub': self.token
            }
            auth_token = jwt.encode(payload,
                                    self.secret_key,
                                    algorithm='HS256').decode("utf-8")
        return auth_token

    def configure_token(self, secret_key):
        self.secret_key = secret_key
