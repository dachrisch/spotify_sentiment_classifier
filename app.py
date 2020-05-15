import json
import os
from logging import config, getLogger

from flask import Flask

from sentiment.web import create_app


def run_gunicorn():
    app = create_app()
    _configure_logging(app)
    return app


def run_flask():
    app = create_app()
    _configure_logging(app)

    if app.config.get('DEBUG'):
        app.run(debug=True, ssl_context='adhoc')
    else:
        app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), ssl_context='adhoc')


def _configure_logging(app: Flask):
    with open('app_logging.json') as f:
        config.dictConfig(json.load(f)['logging'])
    log = getLogger(__name__)
    log.debug('following endpoints are available')
    [log.debug(repr(p)) for p in app.url_map.iter_rules()]


if __name__ == '__main__':
    run_flask()
