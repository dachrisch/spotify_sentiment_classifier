import json
import random
from importlib import resources

import spotipy

from spotify.service import SpotifyAuthenticationService, SpotifyMoodClassificationService


class SpotifyTestConnector(spotipy.Spotify):
    def __init__(self):
        super().__init__()
        self._session = None
        self.playlists = {'items': []}
        self.tracks_in_playlists = {}

    def current_user_playlists(self, limit=50, offset=0):
        return self.playlists

    def current_user(self):
        return {'display_name': '1121820983', 'external_urls': {'spotify': 'https://open.spotify.com/user/1121820983'},
                'followers': {'href': None, 'total': 23}, 'href': 'https://api.spotify.com/v1/users/1121820983',
                'id': '1121820983', 'images': [], 'type': 'user', 'uri': 'spotify:user:1121820983'}

    def user_playlist_create(self, user, name, public=True, description=""):
        playlist_id = random.randint(0, 100000)
        self.playlists['items'].append({'name': name, 'playlist_id': playlist_id})
        return {'playlist_id': playlist_id}

    def audio_features(self, tracks=None):
        with resources.open_text('fixures', 'user_tracks_features.json5') as tracks_features:
            return json.load(tracks_features)

    def playlist_tracks(self,
                        playlist_id,
                        fields=None,
                        limit=100,
                        offset=0,
                        market=None,
                        additional_types=("track",)):
        return self.tracks_in_playlists[playlist_id]

    def user_playlist_add_tracks(self, user, playlist_id, tracks, position=None):
        for track in tracks:
            if playlist_id not in self.tracks_in_playlists:
                self.tracks_in_playlists[playlist_id] = {'items': []}
            self.tracks_in_playlists[playlist_id]['items'].append(
                {'track': {'id': track, 'name': playlist_id}})

    def current_user_saved_tracks(self, limit=20, offset=0):
        with resources.open_text('fixures', 'current_user_tracks.json5') as user_tracks_file:
            return json.load(user_tracks_file)


class SpotifyAuthenticationTestService(SpotifyAuthenticationService):
    def __init__(self):
        self.connector = SpotifyTestConnector()

    def with_token(self, token):
        return SpotifyMoodClassificationService(self.connector)
