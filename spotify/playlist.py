import logging

import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    log = logging.getLogger(__name__)

    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.user_id = self.spotify_connector.current_user()['id']

    def tracks_in_playlist(self, sentiment: Sentiment):
        playlist_for_sentiment = self.playlist_for_sentiment(sentiment)
        if playlist_for_sentiment:
            return self.spotify_connector.playlist_tracks(playlist_for_sentiment['id'],
                                                          fields='items(track(name,id))')['items']
        else:
            return ()

    def add_tracks_to_playlist(self, track_ids, sentiment: Sentiment):
        playlist_for_sentiment = self.playlist_for_sentiment(sentiment)
        if not playlist_for_sentiment:
            playlist_for_sentiment = self.__create_playlist(sentiment)
        self.log.debug('adding [%d] tracks to playlist [%s]' % (len(track_ids), playlist_for_sentiment))
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

    @staticmethod
    def map_names(dict_with_names: dict):
        return tuple(map(lambda x: x['name'], dict_with_names))

    def __create_playlist(self, sentiment: Sentiment):
        playlist_name = PlaylistManager.to_playlist(sentiment)
        self.log.debug('creating playlist [%s]' % playlist_name)
        return self.spotify_connector.user_playlist_create(self.user_id, playlist_name, False)

    def playlist_for_sentiment(self, sentiment: Sentiment):
        playlist = None
        playlists = self.spotify_connector.current_user_playlists()['items']
        if playlists:
            playlists_for_sentiment = list(
                filter(lambda x: x['name'] == PlaylistManager.to_playlist(sentiment), playlists))
            if playlists_for_sentiment and len(playlists_for_sentiment) == 1:
                playlist = playlists_for_sentiment[0]

        return playlist

    def get_playlist_uri(self, sentiment):
        return 'spotify:track:2DB2zVP1LVu6jjyrvqD44z'
