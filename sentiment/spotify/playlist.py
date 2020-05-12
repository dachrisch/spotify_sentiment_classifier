import logging

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.connector import SpotipyConnectionWrapper


class PlaylistManager(object):

    def __init__(self, spotify_connector: SpotipyConnectionWrapper):
        self.spotify_connector = spotify_connector
        self.user_id = self.spotify_connector.current_user()['id']
        self.log = logging.getLogger(__name__)

    def tracks_in_playlist(self, sentiment: Sentiment):
        playlist_for_sentiment = self.playlist_for_sentiment(sentiment)
        tracks = ()
        if playlist_for_sentiment:
            tracks = self.spotify_connector.playlist_tracks(playlist_for_sentiment['id'],
                                                            fields='items(track(name,id))')['items']
        self.log.debug('found [{}] tracks in playlist [{}]'.format(len(tracks), sentiment))
        return tracks

    def add_tracks_to_playlist(self, track_ids, sentiment: Sentiment):
        if track_ids:
            playlist_for_sentiment = self.playlist_for_sentiment(sentiment)
            if not playlist_for_sentiment:
                playlist_for_sentiment = self.__create_playlist(sentiment)
            self.log.debug('adding [%s] tracks to playlist [%s]' % (track_ids, playlist_for_sentiment))
            self.spotify_connector.user_playlist_add_tracks(self.user_id, playlist_for_sentiment['id'], track_ids)

    @staticmethod
    def to_playlist(sentiment: Sentiment):
        return {
            Sentiment.DENIAL: 'gm_mood_1',
            Sentiment.ANGER: 'gm_mood_2',
            Sentiment.BARGAINING: 'gm_mood_3',
            Sentiment.DEPRESSION: 'gm_mood_4',
            Sentiment.ACCEPTANCE: 'gm_mood_5',
        }[sentiment]

    def __create_playlist(self, sentiment: Sentiment):
        playlist_name = PlaylistManager.to_playlist(sentiment)
        self.log.debug('creating playlist [%s]' % playlist_name)
        return self.spotify_connector.user_playlist_create(self.user_id, playlist_name, False)

    def playlist_for_sentiment(self, sentiment: Sentiment):
        playlist = None
        playlists = self.spotify_connector.current_user_playlists()['items']
        self.log.debug('current user has [{}] playlists...'.format(len(playlists)))
        if playlists:
            playlists_for_sentiment = list(
                filter(lambda x: x['name'] == PlaylistManager.to_playlist(sentiment), playlists))
            self.log.debug('found [{}] playlists for [{}]'.format(len(playlists_for_sentiment), sentiment))
            if playlists_for_sentiment and len(playlists_for_sentiment) == 1:
                playlist = playlists_for_sentiment[0]

        self.log.debug('sentiment playlist for [{}]: {}'.format(sentiment, playlist))
        return playlist

