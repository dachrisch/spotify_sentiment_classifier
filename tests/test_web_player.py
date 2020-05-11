from unittest import TestCase

from bs4 import BeautifulSoup

from sentiment.classify.sentiment import Sentiment
from sentiment.web.views import MoodPlayerView
from tests.web_testing_base import WithTestClientMixin


class TestWebPlayer(TestCase, WithTestClientMixin):

    def setUp(self):
        self._setup_testclient()

    def test_login_shown_when_not_logged_in(self):
        response = self.test_client.get('/player/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        button = soup.find(id='spotify_login')
        self.assertIsNotNone(button)
        self.assertIn('Login with Spotify', button.next)

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
        response = self.test_client.get('/player/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        spotify_player = soup.find(id='spotify_player')

        self.assertIsNone(spotify_player)

    def test_error_message(self):
        # setup error
        with self.test_client.session_transaction() as session:
            session['_flashes'] = [('error', "Analyse failed! You don't have any saved tracks."), ]

        # check if error message present
        response = self.test_client.get('/player/', follow_redirects=False)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.data, features='html.parser')
        error_messages = soup.find(id='error_messages')

        self.assertIsNotNone(error_messages)
        self.assertIn('''Analyse failed! You don't have any saved tracks.''', error_messages.contents[1].next)
