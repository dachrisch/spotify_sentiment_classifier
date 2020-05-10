import unittest

from bs4 import BeautifulSoup

from classify.sentiment import Sentiment
from tests.test_analyse_web import WithTestClientMixin
from web.views import HomeView, MoodPlayerView


class TestHomeWeb(unittest.TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_homepage(self):
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        self.assertIn(b'<h1>Sentiment player for your favorite music</h1>', response.data)

    def test_token_expired(self):
        self.storage.token['expires_in'] = -1

        response = self.test_client.post('/analyse/', follow_redirects=False)
        self.assertEqual(302, response.status_code)
        self.assertIn(b'<a href="/login/spotify">', response.data)

    def test_button_active_when_not_analysed(self):
        response = self.test_client.get('/player/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        button = soup.find(id='btn_analyse')
        self.assertIsNotNone(button)
        self.assertIn('Analyse your music library', button.next)

    def test_button_deactivated_when_analysed(self):
        self._setup_account_as_analysed()

        response = self.test_client.get('/player/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        button = soup.find(id='btn_analysed')
        self.assertIsNotNone(button)
        self.assertIn('Music library analysed', button.next)

    def _setup_account_as_analysed(self):
        for sentiment in Sentiment:
            HomeView.service.with_token(None).playlist_manager.add_tracks_to_playlist(('2p9RbgJwcuxasdMrQBdDDA3p',),
                                                                                      sentiment)
            MoodPlayerView.service.with_token(None).playlist_manager.add_tracks_to_playlist(
                ('2p9RbgJwcuxasdMrQBdDDA3p',),
                sentiment)

    def test_press_sentiment_button(self):
        self._setup_account_as_analysed()
        response = self.test_client.post('/player/', follow_redirects=False, data={'ANGER': True})

        self.assertEqual(200, response.status_code)

    def test_playlist_is_anger(self):
        self._setup_account_as_analysed()
        response = self.test_client.post('/player/', follow_redirects=False, data={'ANGER': True})

        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        spotify_player = soup.find(id='spotify_player')
        expected_id = MoodPlayerView.service.with_token(None).playlist_manager.playlist_for_sentiment(Sentiment.ANGER)[
            'id']
        self.assertEqual('https://open.spotify.com/embed/playlist/{}'.format(expected_id), spotify_player.attrs['src'])

    def test_no_player_when_no_playlist_on_homepage(self):
        self._setup_account_as_analysed()
        response = self.test_client.get('/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        spotify_player = soup.find(id='spotify_player')

        self.assertIsNone(spotify_player)

    def test_message_is_displayed(self):
        response = self.test_client.get('/?error="Test"', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        error_messages = soup.find(id='error_messages')

        self.assertIsNotNone(error_messages)
