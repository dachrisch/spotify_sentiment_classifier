import logging

from flask_restx import Api

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Sentiment API',
          description='Get Sentiments for Spotify')
