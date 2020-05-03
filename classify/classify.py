import logging

import spotipy

from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


class FeatureClassifier(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector

    def classify(self, song_feature):
        valence = song_feature['valence']
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
    def __init__(self, spotify_connector: spotipy.Spotify, classifier: FeatureClassifier):
        self.classifier = classifier
        self.spotify_connector = spotify_connector
        self.playlist_manager = PlaylistManager(self.spotify_connector)
        self.log = logging.getLogger(__name__)

    def perform(self):
        all_song_ids = set(map(lambda x: x['track']['id'], self.spotify_connector.current_user_saved_tracks()['items']))

        self.log.info('analyzing [%s] current songs for sentiment...' % (len(all_song_ids)))
        all_song_features = self.spotify_connector.audio_features(all_song_ids)

        for sentiment in Sentiment:
            songs_in_sentiment = tuple(
                filter(lambda song_features: self.classifier.classify(song_features) == sentiment, all_song_features))
            self.log.debug('songs found for sentiment [%s]: %d' % (sentiment.name, len(songs_in_sentiment)))
            self.playlist_manager.add_songs_to_playlist(
                set(map(lambda song_features: song_features['id'],
                        songs_in_sentiment)),
                sentiment)