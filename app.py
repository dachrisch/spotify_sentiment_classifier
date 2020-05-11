import json
import os
from logging import config, getLogger

from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_dance.contrib.spotify import make_spotify_blueprint
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from api.restplus import api
from web.views import HomeView, MoodPlayerView, AnalyseView


def create_app():
    flask_app = Flask(__name__)

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)

    flask_app.secret_key = '12345'

    configure_app(flask_app)
    add_views(flask_app)
    app_api(flask_app)
    app_spotify_login(flask_app)
    add_security(flask_app)

    Bootstrap(flask_app)

    return flask_app


def configure_app(flask_app):
    app_config = {
        'development': 'config.DevelopmentConfig',
        'testing': 'config.TestingConfig',
        'production': 'config.ProductionConfig',
        'default': 'config.DevelopmentConfig'
    }
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    flask_app.config.from_object(app_config[config_name])


def add_security(flask_app):
    csp = {
        'default-src': "'self'",
        'img-src': '*',
        'style-src': ("'self'", 'https://fonts.googleapis.com/css'),
        'font-src': ("'self'", 'fonts.gstatic.com'),
        'script-src': "'self'"
    }
    Talisman(flask_app, content_security_policy=csp)


def app_spotify_login(flask_app):
    spotify_blueprint = make_spotify_blueprint(os.getenv("SPOTIPY_CLIENT_ID"), os.getenv("SPOTIPY_CLIENT_SECRET"),
                                               'user-library-read playlist-modify-private playlist-read-private '
                                               'user-modify-playback-state user-read-playback-state',
                                               os.getenv("SPOTIPY_REDIRECT_URI"))
    flask_app.register_blueprint(spotify_blueprint, url_prefix='/login')


def add_views(flask_app):
    HomeView.register(flask_app)
    AnalyseView.register(flask_app)
    MoodPlayerView.register(flask_app)


def app_api(flask_app):
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(api_blueprint)
    # import this, so it gets initialized
    from api.endpoints.sentiment import ns
    assert ns.name == 'sentiment', ns.name
    flask_app.register_blueprint(api_blueprint)


if __name__ == '__main__':
    with open('app_logging.json') as f:
        config.dictConfig(json.load(f)['logging'])

    app = create_app()

    log = getLogger(__name__)
    log.debug('following endpoints are available')
    [log.debug(repr(p)) for p in app.url_map.iter_rules()]

    if app.config.get('DEBUG'):
        app.run(debug=True, ssl_context='adhoc')
    else:
        app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), debug=True, ssl_context='adhoc')
