import logging

import spotipy

from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


class FeatureClassifier(object):

    @staticmethod
    def classify(track_feature):
        valence = track_feature['valence']
        if 0 <= valence < .2:
            return Sentiment.DEPRESSION
        elif .2 <= valence < .4:
            return Sentiment.ANGER
        elif .4 <= valence < .5:
            return Sentiment.DENIAL
        elif .5 <= valence < .6:
            return Sentiment.BARGAINING
        elif .6 <= valence <= 1:
            return Sentiment.ACCEPTANCE


class SpotifyMoodClassification(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.playlist_manager = PlaylistManager(self.spotify_connector)
        self.log = logging.getLogger(__name__)

    def analyse(self):
        all_tracks = tuple(map(lambda x: x['track'], self.spotify_connector.current_user_saved_tracks()['items']))
        all_tracks_ids = tuple(map(lambda x: x['id'], all_tracks))

        self.log.info('analyzing [%s] tracks for sentiment...' % (len(all_tracks_ids)))
        all_tracks_features = self.spotify_connector.audio_features(all_tracks_ids)

        for sentiment in Sentiment:
            tracks_features_in_sentiment = tuple(
                filter(lambda x: FeatureClassifier.classify(x) == sentiment, all_tracks_features))
            track_ids_in_sentiment = set(map(lambda x: x['id'], tracks_features_in_sentiment))
            self.log.info('tracks found for [%s]: %d' % (sentiment.name, len(tracks_features_in_sentiment)))
            self.log.debug(list(map(lambda y: {'id': y['id'], 'name': y['name']},
                                    filter(lambda x: x['id'] in track_ids_in_sentiment, all_tracks))))
            self.playlist_manager.add_tracks_to_playlist(track_ids_in_sentiment, sentiment)


class SpotifyAuthentificationService(object):
    def with_token(self, token):
        sp = spotipy.Spotify(auth=token)

        return SpotifyMoodClassification(sp)
