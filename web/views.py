import logging

from flask import render_template, request, url_for
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField

from classify.sentiment import Sentiment
from spotify.service import SpotifyAuthenticationService, SpotifyMoodClassificationService


class WithSpotifyServiceMixin(object):
    service = SpotifyAuthenticationService()

    def __init__(self):
        self.spotify_service: SpotifyMoodClassificationService = None

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
            'user is {}'.format(self._valid_login() and 'logged in' or 'not logged in'))
        return render_template('homepage.html')


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


class MoodPlayerView(FlaskView, WithSpotifyServiceMixin):
    route_base = '/player'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def index(self):
        self.log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        form = SentimentForm(request.form)
        return render_template('player.html', form=form, is_analysed=(self._is_analysed()))

    def post(self):
        self.log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        form = SentimentForm(request.form)
        sentiment_name = None
        if form.is_submitted():
            for name, value in form.data.items():
                if value:
                    sentiment_name = name
                    break
        playlist_id = None
        if sentiment_name:
            sentiment = Sentiment.__getitem__(sentiment_name)
            playlist_id = self.spotify_service.playlist_manager.playlist_for_sentiment(sentiment)['id']
        return render_template('player.html', form=form, playlist_id=playlist_id, is_analysed=(self._is_analysed()))

    def _is_analysed(self):
        return self.spotify_service and self.spotify_service.is_analysed()


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
