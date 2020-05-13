import logging

from flask import render_template, request, url_for, flash, session
from flask_classful import FlaskView
from flask_dance.contrib.spotify import spotify
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import SubmitField

from sentiment.classify.sentiment import Sentiment
from sentiment.spotify.service import SpotifyAuthenticationService, SpotifyMoodClassificationService, \
    UserHasNoTracksException


class WithSpotifyServiceMixin(object):
    service = SpotifyAuthenticationService()

    def __init__(self):
        self.spotify_service: SpotifyMoodClassificationService = None

    def before_request(self, name):
        if self._valid_login():
            self.spotify_service = self.service.with_token(spotify.token)
        else:
            self.spotify_service = None

    def _valid_login(self):
        if spotify.token and 'expires_in' in spotify.token:
            return spotify.authorized and (spotify.token['expires_in'] > 0)
        else:
            return spotify.authorized


class HomeView(FlaskView, WithSpotifyServiceMixin):
    route_base = '/'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def index(self):
        if session.get('next_url'):
            return redirect(session.pop('next_url'))
        self.log.debug('user is {}'.format(self._valid_login() and 'logged in' or 'not logged in'))
        return render_template('homepage.html')


class LoginView(FlaskView):
    route = '/login'

    def index(self):
        session['next_url'] = request.args.get('next')
        return redirect(url_for('spotify.login'))


class AnalyseView(FlaskView, WithSpotifyServiceMixin):
    route = '/analyse'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def post(self):
        if not self._valid_login():
            self.log.debug('redirecting for authentication...')
            return redirect(url_for('LoginView:index', next=url_for('AnalyseView:post')))
        try:
            self.spotify_service.analyse()
            return redirect(url_for('MoodPlayerView:index'))
        except UserHasNoTracksException as e:
            self.log.exception(e)
            flash("Analyse failed! You don't have any saved tracks.", 'error')
            return redirect(url_for('MoodPlayerView:index'))


class MoodPlayerView(FlaskView, WithSpotifyServiceMixin):
    route_base = '/player'

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def index(self):
        return self.post()

    def post(self):
        self.log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        form = SentimentForm(request.form)
        playlist_id = self._playlist_id_from_form(form)
        return render_template('player.html', form=form, is_loggedin=self._valid_login(),
                               is_analysed=(self._is_analysed()), username=self._username_if_loggedin(),
                               playlist_id=playlist_id)

    def _username_if_loggedin(self):
        return self.spotify_service and self.spotify_service.username()

    def _playlist_id_from_form(self, form: FlaskForm):
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
        return playlist_id

    def _is_analysed(self):
        return self.spotify_service and self.spotify_service.is_analysed()


class SliderView(FlaskView):
    route = '/slider'

    def index(self):
        return render_template('hello_slider.html')


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
