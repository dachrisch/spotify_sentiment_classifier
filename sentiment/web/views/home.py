from flask import session, render_template
from flask_classful import FlaskView
from werkzeug.utils import redirect

from sentiment.web.auth import SpotifyServiceMixin
from sentiment.web.base import DebugLogMixin


class HomeView(FlaskView, SpotifyServiceMixin, DebugLogMixin):
    route_base = '/'

    def __init__(self):
        super().__init__()

    def index(self):
        if session.get('next_url'):
            return redirect(session.pop('next_url'))
        return render_template('homepage.html')
