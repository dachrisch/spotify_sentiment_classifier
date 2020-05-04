import logging

import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.log = logging.getLogger(__name__)
        self.__playlist_ids = self.__obtain_playlists()

    def available_playlist_names(self):
        return tuple(map(lambda x: x['name'], self._available_playlists()))

    def _available_playlists(self):
        return self.spotify_connector.current_user_playlists()['items']

    def create_playlists(self):
        mood_lists = (self.to_playlist(sentiment) for sentiment in Sentiment)
        available_playlist_names = self.available_playlist_names()
        for list_name in filter(lambda x: x not in available_playlist_names, mood_lists):
            self.log.debug('creating playlist [%s]' % list_name)
            self.spotify_connector.user_playlist_create(self.spotify_connector.current_user()['id'], list_name, False)

    def tracks_in_playlist(self, sentiment: Sentiment):
        return self.spotify_connector.playlist_tracks(self.__playlist_ids[sentiment], fields='items(track(name,id))')[
            'items']

    def add_tracks_to_playlist(self, track_ids, sentiment: Sentiment):
        self.log.debug('adding [%d] tracks to playlist [%s]' % (len(track_ids), self.__playlist_ids[sentiment]))
        self.spotify_connector.user_playlist_add_tracks(self.spotify_connector.current_user()['id'],
                                                        self.__playlist_ids[sentiment], track_ids)

    @staticmethod
    def to_playlist(sentiment: Sentiment):
        return {
            Sentiment.DENIAL: 'gm_mood_1',
            Sentiment.ANGER: 'gm_mood_2',
            Sentiment.BARGAINING: 'gm_mood_3',
            Sentiment.DEPRESSION: 'gm_mood_4',
            Sentiment.ACCEPTANCE: 'gm_mood_5',
        }[sentiment]

    def __obtain_playlists(self):
        self.create_playlists()

        playlists = self._available_playlists()
        playlist_mapping = {}
        for sentiment in Sentiment:
            sentiment_playlist = list(filter(lambda x: x['name'] == self.to_playlist(sentiment), playlists))
            playlist_mapping[sentiment] = sentiment_playlist[0]['id']

        return playlist_mapping
