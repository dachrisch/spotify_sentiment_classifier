import json
import logging
import os
from logging import config

from flask import render_template, Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_dance.contrib.spotify import make_spotify_blueprint

from api.restplus import api

global user_token

def create_app():
    flask_app = Flask(__name__)

    flask_app.secret_key = '12345'

    add_homepage(flask_app)
    app_api(flask_app)

    spotify_blueprint = make_spotify_blueprint(os.getenv("SPOTIPY_CLIENT_ID"), os.getenv("SPOTIPY_CLIENT_SECRET"),
                                               'user-library-read playlist-modify-private',
                                               os.getenv("SPOTIPY_REDIRECT_URI"))

    flask_app.register_blueprint(spotify_blueprint, url_prefix='/login')
    Bootstrap(flask_app)
    return flask_app


def add_homepage(flask_app):
    @flask_app.route('/')
    def homepage():
        return render_template('homepage.html')


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

    log = logging.getLogger(__name__)
    log.debug('following endpoints are availabe')
    [log.debug(repr(p)) for p in app.url_map.iter_rules()]
    app.run(debug=True, ssl_context='adhoc')
