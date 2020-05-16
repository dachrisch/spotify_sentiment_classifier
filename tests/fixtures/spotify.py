import json
import random
import re
from importlib import resources
from pathlib import PurePosixPath

import spotipy as spotipy
from bunch import Bunch

from sentiment.spotify.connector import SpotipyConnectionWrapper
from sentiment.spotify.service import SpotifyAuthenticationService, SpotifyMoodClassificationService


class NoTracksException(Exception):
    pass


class SpotipyTestFixture(spotipy.Spotify):
    @classmethod
    def as_wrapper(cls):
        return SpotipyConnectionWrapper(cls())

    def __init__(self):
        super().__init__(None)
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
        playlist_id = str(random.randint(0, 100000))
        self.playlists['items'].append({'name': name, 'id': playlist_id})
        return {'id': playlist_id}

    def audio_features(self, tracks=None):
        with resources.open_text('tests.fixtures', 'user_tracks_features.json5') as tracks_features:
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
        if not tracks:
            raise NoTracksException
        for track in tracks:
            if playlist_id not in self.tracks_in_playlists:
                self.tracks_in_playlists[playlist_id] = {'items': []}
            self.tracks_in_playlists[playlist_id]['items'].append(
                {'track': {'id': track, 'name': playlist_id}})

    def current_user_saved_tracks(self, limit=20, offset=0):
        with resources.open_text('tests.fixtures', 'current_user_tracks.json5') as user_tracks_file:
            return json.load(user_tracks_file)


class SpotifyAuthenticationTestService(SpotifyAuthenticationService):
    def __init__(self):
        super().__init__()
        self._connector = SpotipyConnectionWrapper(SpotipyTestFixture())
        self._service_instance = SpotifyMoodClassificationService(self._connector)

    @property
    def service_instance(self) -> SpotifyMoodClassificationService:
        return self._service_instance


class RequestsMockFixtureMixin(object):
    def _prepare_requests(self, requests_mock):
        fixture = SpotipyTestFixture()
        requests_mock.get('https://api.spotify.com/v1/me/', json=fixture.current_user())
        requests_mock.get('https://api.spotify.com/v1/me/playlists?limit=50&offset=0',
                          json=fixture.current_user_playlists())
        requests_mock.get('https://api.spotify.com/v1/me/tracks?limit=20&offset=0',
                          json=fixture.current_user_saved_tracks())
        requests_mock.get(
            'https://api.spotify.com/v1/audio-features/?ids=6lXKNdOsnaLv9LwulZbxNl,'
            '2p9RbgJwcuxMrQBhdDDA3p,3MVbvj0L7RTJy2CZYtf2c7,5AIYDx0HUjra5Bn0vZtjmd,2rnuW7ZTLSWT54yYvVaKT1',
            json=fixture.audio_features())

        def user_playlist_create_callback(request, context):
            params = Bunch(json.loads(request.text))
            root, version, api_1, username, api_2 = PurePosixPath(request.path).parts
            return fixture.user_playlist_create(username, params.name, params.public, params.description)

        requests_mock.post('https://api.spotify.com/v1/users/1121820983/playlists', json=user_playlist_create_callback)

        def user_playlist_add_tracks_callback(request, context):
            root, version, api_1, username, api_2, playlist_id, api_3 = PurePosixPath(request.path).parts
            return fixture.user_playlist_add_tracks(username, playlist_id,
                                                    list(map(lambda x: x.split(':')[2], json.loads(request.text))))

        requests_mock.post(re.compile('https://api.spotify.com/v1/users/1121820983/playlists/[0-9]+/tracks'),
                           json=user_playlist_add_tracks_callback)

        def playlist_tracks_callback(request, context):
            root, version, api_1, playlist_id, api_2 = PurePosixPath(request.path).parts
            return fixture.playlist_tracks(playlist_id)

        requests_mock.get(
            re.compile(
                'https://api.spotify.com/v1/playlists/[0-9]+/tracks'
                '\?limit=100&offset=0&fields=items%28track%28name%2Cid%29%29&additional_types=track'),
            json=playlist_tracks_callback)
        return fixture
