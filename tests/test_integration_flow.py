import json
import re
import unittest
from pathlib import PurePosixPath
from unittest import TestCase

import requests_mock
from bunch import Bunch

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.connector import SpotipyConnectionWrapper
from sentiment.spotify.playlist import PlaylistManager
from sentiment.web import create_app
from tests.fixtures.spotify import SpotipyTestFixture
from tests.web_testing_base import WithTestClientMixin, ItemValidator


class SpotifyServerMock:

    def __init__(self):
        pass


class TestWebIntegration(TestCase, WithTestClientMixin):

    def setUp(self):
        self.test_app = create_app()

    def test_not_logged_in_from_homepage_to_spotify(self):
        self._run_flow().on('https://localhost').validate_that() \
            .get('/').responds(200) \
            .click_button(id='own_music').responds(200).on_page('/player/') \
            .click_button(id='spotify_login').responds(302).on_page('/login/?next=%2Fplayer%2F') \
            .follow_redirect().to('/login/spotify').follow_redirect().to('https://accounts.spotify.com/authorize')

    @requests_mock.Mocker()
    def test_logged_in_from_homepage_analyse_to_player(self, requests_mock):
        self._setup_logged_in()

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

        validate_that = self._run_flow().on('https://localhost').validate_that().get('/')
        validate_that = validate_that.responds(200)
        validate_that = validate_that.click_button(id='own_music').responds(200).on_page('/player/')
        validate_that = validate_that.submit_button(in_form='analyse_form', id='btn_analyse').on_page(
            '/analyse/').follow_redirect().to('/player/')

        validate_that = validate_that.submit_button(in_form='sentiment_form', id=Sentiment.ANGER.name).responds(
            200).on_page('/player/')
        validate_that = validate_that.has(ItemValidator.attr('src', 'https://open.spotify.com/embed/playlist/{}'.format(
            PlaylistManager(SpotipyConnectionWrapper(fixture)).playlist_for_sentiment(Sentiment.ANGER)['id']
        )), id='spotify_player')


if __name__ == '__main__':
    unittest.main()
