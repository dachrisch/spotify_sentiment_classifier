import logging

import spotipy

from classify.classify import FeatureClassifier
from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


class SpotifyAuthenticationService(object):
    def with_token(self, token):
        sp = spotipy.Spotify(auth=token['access_token'])

        return SpotifyMoodClassificationService(sp)


class UserHasNoTracksException(Exception):
    pass


class SpotifyMoodClassificationService(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
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
        return tuple(filter(lambda x: FeatureClassifier.classify(x) == sentiment, tracks_with_features))

    def _all_tracks_audio_features(self, all_tracks):
        all_tracks_features = self.spotify_connector.audio_features(self._only_ids(all_tracks))
        return all_tracks_features

    def _only_ids(self, tracks):
        return tuple(map(lambda x: x['id'], tracks))

    def _all_tracks(self):
        user_saved_tracks = self.spotify_connector.current_user_saved_tracks()
        self.log.debug('user has the following saved tracks: [{}]'.format(user_saved_tracks))
        return tuple(map(lambda x: x['track'], user_saved_tracks['items']))
