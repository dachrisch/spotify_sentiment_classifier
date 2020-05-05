import logging

from flask import url_for
from flask_dance.contrib.spotify import spotify
from flask_restx import Resource
from werkzeug.utils import redirect

from api.restplus import api
from classify.classify import SpotifyAuthentificationService

log = logging.getLogger(__name__)

ns = api.namespace('sentiment', description='Sentiment Operations for Spotify')


@ns.route('/analyse')
class Analyse(Resource):
    service = SpotifyAuthentificationService()

    def get(self):
        if not spotify.authorized:
            return redirect(url_for('spotify.login'))

        Analyse.service.with_token(spotify.token).analyse()
        return 'Created'
