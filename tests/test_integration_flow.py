import unittest
from unittest import TestCase

from sentiment.web import create_app
from tests.web_testing_base import with_client


class TestWebIntegration(TestCase):

    def test_not_logged_in_from_homepage_to_spotify(self):
        with_client(create_app()).on('https://localhost').validate_that() \
            .get('/').responds(200) \
            .click_button(id='own_music').responds(200).on_page('/player/') \
            .click_button(id='spotify_login').responds(302).on_page('/login/?next=%2Fplayer%2F') \
            .follow_redirect().to('/login/spotify').follow_redirect().to('https://accounts.spotify.com/authorize')


if __name__ == '__main__':
    unittest.main()
