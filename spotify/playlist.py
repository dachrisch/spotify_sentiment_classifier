import logging

import spotipy

from classify.sentiment import Sentiment


class PlaylistManager(object):
    log = logging.getLogger(__name__)

    def __init__(self, spotify_connector: spotipy.Spotify):
        self.spotify_connector = spotify_connector
        self.user_id = self.spotify_connector.current_user()['id']
        self.__playlist_ids = PlaylistManager.__obtain_playlists(self.spotify_connector, self.user_id)

    def tracks_in_playlist(self, sentiment: Sentiment):
        return self.spotify_connector.playlist_tracks(self.__playlist_ids[sentiment], fields='items(track(name,id))')[
            'items']

    def add_tracks_to_playlist(self, track_ids, sentiment: Sentiment):
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

    @staticmethod
    def __create_playlists(spotify_connector: spotipy.Spotify, user_id: str, playlists: dict):
        mood_lists = (PlaylistManager.to_playlist(sentiment) for sentiment in Sentiment)
        available_playlist_names = PlaylistManager.map_names(playlists)
        for list_name in filter(lambda x: x not in available_playlist_names, mood_lists):
            PlaylistManager.log.debug('creating playlist [%s]' % list_name)
            spotify_connector.user_playlist_create(user_id, list_name, False)

    @staticmethod
    def __obtain_playlists(spotify_connector: spotipy.Spotify, user_id: str):
        playlists = spotify_connector.current_user_playlists()['items']
        PlaylistManager.__create_playlists(spotify_connector, user_id, playlists)

        playlist_mapping = {}
        for sentiment in Sentiment:
            sentiment_playlist = list(filter(lambda x: x['name'] == PlaylistManager.to_playlist(sentiment), playlists))
            playlist_mapping[sentiment] = sentiment_playlist[0]['id']

        return playlist_mapping
