import spotipy
from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from werkzeug.utils import redirect

from api.endpoints.sentiment import Analyse
from classify.sentiment import Sentiment
from spotify.player import Player


class HomeView(FlaskView):
    route_base = '/'

    def index(self):
        username = None
        if not spotify.authorized:
            return redirect(url_for('spotify.login'))
        try:
            username = spotipy.Spotify(spotify.token['access_token']).current_user()['display_name']
        except spotipy.SpotifyException as e:
            if 'The access token expired' in e.msg:
                return redirect(url_for('spotify.login'))
        return render_template('homepage.html', username=username, is_analysed=True)


class AnalyseView(FlaskView):
    route = '/analyse'

    def post(self):
        Analyse.service.with_token(spotify.token['access_token']).analyse()
        return redirect(url_for('HomeView:index'))


class MoodPlayerView(FlaskView):
    route_base = '/player'

    def post(self):
        pressed_button = request.args.get('depression_button')
        sentiment = Sentiment.DEPRESSION
        Player(spotipy.Spotify(spotify.token['access_token'])).queue_sentiment_playlist(sentiment)
        return redirect(url_for('HomeView:index'))
