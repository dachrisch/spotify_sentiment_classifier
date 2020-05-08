import spotipy
from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import HiddenField

from api.endpoints.sentiment import Analyse
from classify.sentiment import Sentiment


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

    def index(self):
        button_sentiments = {}
        for sentiment in Sentiment:
            button_sentiments[{
                Sentiment.DENIAL: 'btn-danger',
                Sentiment.ANGER: 'btn-warning',
                Sentiment.BARGAINING: 'btn-info',
                Sentiment.DEPRESSION: 'btn-primary',
                Sentiment.ACCEPTANCE: 'btn-success',
            }[sentiment]] = sentiment.name
        return render_template('mood_player.html', button_sentiments=button_sentiments, form=SentimentForm())

    def post(self):
        form = SentimentForm(request.form)
        return form.sentiment.data


class SentimentForm(FlaskForm):
    sentiment = HiddenField()
