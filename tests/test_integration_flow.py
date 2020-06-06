import unittest
from unittest import TestCase

import requests_mock

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.connector import SpotipyConnectionWrapper
from sentiment.spotify.playlist import PlaylistManager
from sentiment.web import create_app
from tests.fixtures.spotify import RequestsMockFixtureMixin
from tests.web_testing_base import TestClientMixin, ItemValidator


class TestWebIntegration(TestCase, TestClientMixin, RequestsMockFixtureMixin):

    def setUp(self):
        self.test_app = create_app()

    def test_not_logged_in_from_homepage_to_spotify(self):
        self._run_flow().on('https://localhost').validate_that() \
            .get('/').responds(200) \
            .click_button(id='own_music').responds(200).on_page('/player/') \
            .click_button(id='spotify_login').responds(302).on_page('/login/?next=%2Fplayer%2F') \
            .follow_redirect().to('/login/spotify').follow_redirect().to('https://accounts.spotify.com/authorize')

    @requests_mock.Mocker()
    def test_logged_in_from_homepage_analyse_to_player(self, mock):
        self._setup_logged_in()

        fixture = self._prepare_requests(mock)

        validate_that = self._run_flow().on('https://localhost').validate_that().get('/')
        validate_that = validate_that.responds(200)
        validate_that = validate_that.click_button(id='own_music').responds(200).on_page('/player/')
        validate_that = validate_that.submit_button(in_form='analyse_form', id='btn_analyse').on_page(
            '/analyse/').follow_redirect().to('/player/')

        validate_that.has(ItemValidator.attr('src', 'https://open.spotify.com/embed/playlist/{}'.format(
            PlaylistManager(SpotipyConnectionWrapper(fixture)).playlist_for_sentiment(Sentiment.ANGER)['id']
        )), id='spotify_player_{}'.format(Sentiment.ANGER))


if __name__ == '__main__':
    unittest.main()
