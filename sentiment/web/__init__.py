import os

from flask import Flask, Blueprint
from flask_assets import Environment
from flask_bootstrap import Bootstrap
from flask_dance.contrib.spotify import make_spotify_blueprint
from flask_talisman import Talisman
from webassets import Bundle
from werkzeug.middleware.proxy_fix import ProxyFix

from sentiment.api.restplus import api
from sentiment.web.views.analyse import AnalyseView
from sentiment.web.views.home import HomeView
from sentiment.web.views.login import LoginView
from sentiment.web.views.player import MoodPlayerView
from sentiment.web.views.sentiment_config import ConfigView
from sentiment.web.views.slider import SliderView


def create_app():
    flask_app = Flask(__name__, template_folder='../templates', static_folder='../static')

    flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)

    flask_app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

    configure_app(flask_app)
    add_views(flask_app)
    app_api(flask_app)
    app_spotify_login(flask_app)
    add_security(flask_app)
    configure_assets(flask_app)

    Bootstrap(flask_app)

    return flask_app


def configure_assets(flask_app):
    assets = Environment(flask_app)
    style_bundle = Bundle('assets/scss/slider.scss',
                          filters='pyscss',  # https://webassets.readthedocs.io/en/latest/builtin_filters.html#pyscss
                          output='dist/css/slider.min.css',
                          extra={'rel': 'stylesheet/css'})
    assets.register('main_styles', style_bundle)
    js_bundle = Bundle('assets/js/slider.js', 'assets/js/modal.js',
                       filters='rjsmin',  # https://webassets.readthedocs.io/en/latest/builtin_filters.html#rjsmin
                       output='dist/js/custom.min.js')
    assets.register('main_js', js_bundle)
    style_bundle.build()
    js_bundle.build()


def configure_app(flask_app):
    app_config = {
        'development': 'sentiment.config.DevelopmentConfig',
        'testing': 'sentiment.config.TestingConfig',
        'production': 'sentiment.config.ProductionConfig',
        'default': 'sentiment.config.DevelopmentConfig'
    }
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    flask_app.config.from_object(app_config[config_name])


def add_security(flask_app):
    csp = {
        'default-src': "'self'",
        'img-src': '*',
        'style-src': (
            "'self'", 'https://fonts.googleapis.com/css', "'unsafe-inline'", 'ajax.googleapis.com',
            'cdnjs.cloudflare.com'),
        'font-src': ("'self'", 'fonts.gstatic.com', 'data:'),
        'script-src': ("'self'"),
        'frame-src': 'https://open.spotify.com/'
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
    LoginView.register(flask_app)
    SliderView.register(flask_app)
    ConfigView.register(flask_app)


def app_api(flask_app):
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(api_blueprint)
    # import this, so it gets initialized
    from sentiment.api.endpoints.sentiment import ns
    assert ns.name == 'sentiment', ns.name
    flask_app.register_blueprint(api_blueprint)
