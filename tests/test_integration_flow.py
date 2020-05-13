import unittest
from unittest import TestCase

from tests.web_testing_base import WithTestClientMixin, with_client


class TestWebIntegration(TestCase, WithTestClientMixin):
    def setUp(self):
        self._setup_testclient()

    def test_not_logged_in_from_homepage_to_spotify(self):
        with self.test_app.test_client() as client:
            with_client(client).on('https://localhost').validate_that() \
                .get('/').responds(200) \
                .click_button(id='own_music').responds(200).on_page('/player/') \
                .click_button(id='spotify_login').responds(302).on_page('/login/?next=%2Fplayer%2F') \
                .follow_redirect().to('/login/spotify').follow_redirect().to('https://accounts.spotify.com/authorize')


if __name__ == '__main__':
    unittest.main()
