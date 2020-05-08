import logging

from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField

from classify.sentiment import Sentiment
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
        return render_template('homepage.html', is_analysed=(self._is_analysed()), form=SentimentForm(request.form))

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
        form = SentimentForm()
        # Player(spotipy.Spotify(spotify.token['access_token'])).queue_sentiment_playlist(sentiment)
        return redirect(url_for('HomeView:index'))


def with_sentiment_buttons(cls):
    for sentiment in Sentiment:
        setattr(cls, sentiment.name, SubmitField(sentiment.name))
    return cls


@with_sentiment_buttons
class SentimentForm(FlaskForm):

    def __init__(self, form=None):
        super(SentimentForm, self).__init__(form)

    def sentiment_buttons(self):
        for sentiment in Sentiment:
            yield getattr(self, sentiment.name)
