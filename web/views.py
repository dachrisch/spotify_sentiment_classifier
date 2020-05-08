import logging

import spotipy
from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from werkzeug.utils import redirect

from classify.sentiment import Sentiment
from spotify.player import Player
from spotify.service import SpotifyAuthenticationService


class HomeView(FlaskView):
    route_base = '/'
    service = SpotifyAuthenticationService()

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.spotify_service = None

    def before_request(self, name):
        self.spotify_service = self.service.with_token(spotify.token)

    def index(self):
        if not self._valid_login():
            self.log.debug('redirecting for authentication...')
            return redirect(url_for('spotify.login'))

        self.log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        return render_template('homepage.html', is_analysed=(self._is_analysed()))

    def _is_analysed(self):
        return self._valid_login() and self.spotify_service.is_analysed()

    def _valid_login(self):
        return spotify.authorized and (spotify.token['expires_in'] > 0)


class AnalyseView(FlaskView):
    route = '/analyse'
    service = SpotifyAuthenticationService()

    def post(self):
        AnalyseView.service.with_token(spotify.token).analyse()
        return redirect(url_for('HomeView:index'))


class MoodPlayerView(FlaskView):
    route_base = '/player'

    def post(self):
        pressed_button = request.args.get('depression_button')
        sentiment = Sentiment.DEPRESSION
        Player(spotipy.Spotify(spotify.token['access_token'])).queue_sentiment_playlist(sentiment)
        return redirect(url_for('HomeView:index'))
