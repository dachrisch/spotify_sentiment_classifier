from functools import lru_cache

import spotipy


class SpotipyConnectionWrapper(object):
    @classmethod
    def from_token(cls, access_token):
        return cls(spotipy.Spotify(auth=access_token))

    def __init__(self, to_wrap: spotipy.Spotify):
        self.__connection = to_wrap

    @lru_cache(128)
    def current_user(self):
        return self.__connection.current_user()

    @lru_cache(128)
    def user_playlist_add_tracks(self, user_id, playlist_id, track_ids):
        return self.__connection.user_playlist_add_tracks(user_id, playlist_id, track_ids)

    @lru_cache(128)
    def current_user_playlists(self, limit=50, offset=0):
        return self.__connection.current_user_playlists(limit, offset)

    @lru_cache(128)
    def current_user_saved_tracks(self, limit=20, offset=0):
        return self.__connection.current_user_saved_tracks(limit, offset)

    @lru_cache(128)
    def playlist_tracks(self, playlist_id, fields):
        return self.__connection.playlist_tracks(playlist_id, fields=fields)

    @lru_cache(128)
    def user_playlist_create(self, user, name, public=True, description=""):
        return self.__connection.user_playlist_create(user, name, public=public, description=description)

    @lru_cache(128)
    def audio_features(self, tracks=None):
        return self.__connection.audio_features(tracks)
