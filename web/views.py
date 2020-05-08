import spotipy
from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from werkzeug.utils import redirect

from classify.sentiment import Sentiment
from spotify.player import Player
from spotify.service import SpotifyAuthentificationService


class HomeView(FlaskView):
    route_base = '/'
    service = SpotifyAuthentificationService()

    def index(self):
        if not spotify.authorized:
            return redirect(url_for('spotify.login'))
        username = HomeView.service.with_token(spotify.token['access_token']).username()
        return render_template('homepage.html', username=username, is_analysed=True)


class AnalyseView(FlaskView):
    route = '/analyse'
    service = SpotifyAuthentificationService()

    def post(self):
        AnalyseView.service.with_token(spotify.token['access_token']).analyse()
        return redirect(url_for('HomeView:index'))


class MoodPlayerView(FlaskView):
    route_base = '/player'

    def post(self):
        pressed_button = request.args.get('depression_button')
        sentiment = Sentiment.DEPRESSION
        Player(spotipy.Spotify(spotify.token['access_token'])).queue_sentiment_playlist(sentiment)
        return redirect(url_for('HomeView:index'))
