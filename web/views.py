import logging

import spotipy
from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from werkzeug.utils import redirect

from classify.sentiment import Sentiment
from spotify.player import Player
from spotify.service import SpotifyAuthenticationService


class WithSpotifyServiceMixin(object):
    service = SpotifyAuthenticationService()

    def __init__(self):
        self.spotify_service = None

    def before_request(self, name):
        if self._valid_login():
            self.spotify_service = self.service.with_token(spotify.token)

    def _valid_login(self):
        return spotify.authorized and (spotify.token['expires_in'] > 0)


class HomeView(FlaskView, WithSpotifyServiceMixin):
    route_base = '/'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def index(self):
        self.log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        self.log.debug(
            'user is {}'.format(self._valid_login() and 'logged in' or 'not logged in'))
        return render_template('homepage.html', is_analysed=(self._is_analysed()))

    def _is_analysed(self):
        return self.spotify_service and self.spotify_service.is_analysed()


class AnalyseView(FlaskView, WithSpotifyServiceMixin):
    route = '/analyse'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def post(self):
        if not self._valid_login():
            self.log.debug('redirecting for authentication...')
            return redirect(url_for('spotify.login'))
        AnalyseView.service.with_token(spotify.token).analyse()
        return redirect(url_for('HomeView:index'))


class MoodPlayerView(FlaskView):
    route_base = '/player'

    def post(self):
        pressed_button = request.args.get('depression_button')
        sentiment = Sentiment.DEPRESSION
        Player(spotipy.Spotify(spotify.token['access_token'])).queue_sentiment_playlist(sentiment)
        return redirect(url_for('HomeView:index'))
