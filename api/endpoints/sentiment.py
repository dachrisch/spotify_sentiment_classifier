import logging

import spotipy
from flask import url_for
from flask_dance.contrib.spotify import spotify
from flask_restx import Resource
from werkzeug.utils import redirect

from api.restplus import api
from spotify.service import SpotifyAuthenticationService

ns = api.namespace('sentiment', description='Sentiment Operations for Spotify')


@ns.route('/analyse')
class Analyse(Resource):
    log = logging.getLogger(__name__)
    service = SpotifyAuthenticationService()

    def post(self):
        if not spotify.authorized:
            return redirect(url_for('spotify.login'))

        try:
            self.log.info('invoking sentiment analyse...')
            Analyse.service.with_token(spotify.token['access_token']).analyse()
        except spotipy.SpotifyException as e:
            if 'The access token expired' in e.msg:
                self.log.debug('token expired, re-login...')
                return redirect(url_for('spotify.login'))
            self.log.exception(e)
            raise
        return 'Created'
