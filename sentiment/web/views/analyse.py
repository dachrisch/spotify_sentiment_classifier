from flask import url_for, flash
from flask_classful import FlaskView
from werkzeug.utils import redirect

from sentiment.spotify.service import UserHasNoTracksException
from sentiment.web.auth import SpotifyServiceMixin
from sentiment.web.base import DebugLogMixin


class AnalyseView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/analyse'

    def __init__(self):
        super().__init__()

    def post(self):
        if not self._valid_login():
            self._log.debug('redirecting for authentication...')
            return redirect(url_for('LoginView:index', next=url_for('AnalyseView:post')))
        try:
            self.auth_service.service_instance.analyse()
            return redirect(url_for('MoodPlayerView:index'))
        except UserHasNoTracksException as e:
            self._log.exception(e)
            flash("Analyse failed! You don't have any saved tracks.", 'error')
            return redirect(url_for('MoodPlayerView:index'))
