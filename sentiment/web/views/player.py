from flask import request, render_template
from flask_classful import FlaskView
from flask_wtf import FlaskForm
from wtforms import SubmitField

from sentiment.classify.sentiment import Sentiment
from sentiment.web.auth import SpotifyServiceMixin
from sentiment.web.base import DebugLogMixin


class MoodPlayerView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/player'

    def __init__(self):
        super().__init__()

    def index(self):
        return self.post()

    def post(self):
        self._log.debug(
            'library is {}'.format(self._is_analysed() and 'analysed' or 'not analysed'))
        form = SentimentForm(request.form)
        return render_template('player.html', form=form, is_loggedin=self._valid_login(),
                               is_analysed=(self._is_analysed()), username=self._username_if_logged_in(),
                               playlist_id=(self._playlist_id_from_form(form)), auth_token=self.auth_service.auth_token)

    def _username_if_logged_in(self):
        return self._valid_login() and self.auth_service.service_instance.username()

    def _playlist_id_from_form(self, form: FlaskForm):
        sentiment_name = None
        if self._is_analysed() and form.is_submitted():
            for name, value in form.data.items():
                if value:
                    sentiment_name = name
                    break
        playlist_id = None
        if sentiment_name:
            sentiment = Sentiment.__getitem__(sentiment_name)
            playlist_id = self.auth_service.service_instance.playlist_manager.playlist_for_sentiment(sentiment)['id']
        return playlist_id

    def _is_analysed(self):
        return self._valid_login() and self.auth_service.service_instance.is_analysed()


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
