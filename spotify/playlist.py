import logging

import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    log = logging.getLogger(__name__)

    def __init__(self, spotify_connector: spotipy.Spotify):
        self.__playlist_ids = {}
        self.spotify_connector = spotify_connector
        self.user_id = self.spotify_connector.current_user()['id']

    def tracks_in_playlist(self, sentiment: Sentiment):
        return self.spotify_connector.playlist_tracks(self.__playlist_id_for(sentiment), fields='items(track(name,id))')[
            'items']

    def add_tracks_to_playlist(self, track_ids, sentiment: Sentiment):
        if sentiment not in self.__playlist_ids:
            self.__playlist_ids[sentiment] = self.__create_playlist(sentiment)['id']
        self.log.debug('adding [%d] tracks to playlist [%s]' % (len(track_ids), self.__playlist_ids[sentiment]))
        self.spotify_connector.user_playlist_add_tracks(self.user_id, self.__playlist_ids[sentiment], track_ids)

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

    def __create_playlist(self, sentiment:Sentiment):
        playlist_name = PlaylistManager.to_playlist(sentiment)
        self.log.debug('creating playlist [%s]' % playlist_name)
        return self.spotify_connector.user_playlist_create(self.user_id, playlist_name, False)

    def __obtain_playlists(self):
        playlists = self.spotify_connector.current_user_playlists()['items']

        playlist_mapping = {}
        for sentiment in Sentiment:
            sentiment_playlist = list(filter(lambda x: x['name'] == PlaylistManager.to_playlist(sentiment), playlists))
            playlist_mapping[sentiment] = sentiment_playlist[0]['id']

        return playlist_mapping

    def __playlist_id_for(self, sentiment:Sentiment):
        if not self.__playlist_ids:
            self.__playlist_ids = self.__obtain_playlists()

        return self.__playlist_ids[sentiment]
