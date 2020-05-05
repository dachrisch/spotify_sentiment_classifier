import logging

from flask_restx import Resource

from api.restplus import api
from classify.classify import SpotifyAuthentificationService

log = logging.getLogger(__name__)

ns = api.namespace('sentiment', description='Sentiment Operations for Spotify')


@ns.route('/analyse')
class Analyse(Resource):
    service = SpotifyAuthentificationService()

    def post(self):
        Analyse.service.for_user('1121820983').analyse()
        return 'Created'
