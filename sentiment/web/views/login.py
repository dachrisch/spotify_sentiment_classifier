from flask import session, request, url_for
from flask_classful import FlaskView
from werkzeug.utils import redirect

from sentiment.web.base import DebugLogMixin


class LoginView(FlaskView, DebugLogMixin):
    route_base = '/login'

    def index(self):
        session['next_url'] = request.args.get('next')
        return redirect(url_for('spotify.login'))
