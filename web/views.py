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

    def index(self):
        if (not spotify.authorized) or (spotify.token['expires_in'] < 0):
            self.log.debug('redirecting for authentication...')
            return redirect(url_for('spotify.login'))
        spotify_service = HomeView.service.with_token(spotify.token)
        return render_template('homepage.html', username=spotify_service.username(),
                               is_analysed=spotify_service.is_analysed())


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
