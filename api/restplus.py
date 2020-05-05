import logging

from flask_restplus import Api

import settings
from api.auth import UnauthorizedException

log = logging.getLogger(__name__)

api = Api(version='1.0', title='Südsterne Deployments API',
          description='Access to calendar entry with deployments')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(UnauthorizedException)
def handle_custom_exception(error):
    return {'message': 'Not authorized!'}, 401
