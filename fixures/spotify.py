import json

import spotipy

from classify.sentiment import Sentiment
from spotify.playlist import PlaylistManager


class SpotifyTestConnector(spotipy.Spotify):
    def __init__(self):
        self.playlists = {'items': []}
        self.songs_in_playlists = {PlaylistManager(self)._to_playlist(sentiment): {'items': []} for sentiment in
                                   Sentiment}
        self._session = None

    def current_user_playlists(self, limit=50, offset=0):
        return self.playlists

    def current_user(self):
        return {'display_name': '1121820983', 'external_urls': {'spotify': 'https://open.spotify.com/user/1121820983'},
                'followers': {'href': None, 'total': 23}, 'href': 'https://api.spotify.com/v1/users/1121820983',
                'id': '1121820983', 'images': [], 'type': 'user', 'uri': 'spotify:user:1121820983'}

    def user_playlist_create(self, user, name, public=True, description=""):
        self.playlists['items'].append({'name': name})

    def audio_features(self, tracks=[]):
        with open('../fixures/user_tracks_features.json5', 'r') as tracks_features:
            return json.load(tracks_features)

    def playlist_tracks(self,
                        playlist_id,
                        fields=None,
                        limit=100,
                        offset=0,
                        market=None,
                        additional_types=("track",)):
        return self.songs_in_playlists[playlist_id]

    def user_playlist_add_tracks(self, user, playlist_id, tracks, position=None):
        for track in tracks:
            self.songs_in_playlists[playlist_id]['items'].append(
                {'track': {'id': track, 'name': playlist_id.lower()}})

    def current_user_saved_tracks(self, limit=20, offset=0):
        with open('../fixures/current_user_tracks.json5', 'r') as user_tracks_file:
            return json.load(user_tracks_file)
