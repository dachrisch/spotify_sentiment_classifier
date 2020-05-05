import json
import logging
from logging import config

from flask import render_template, Flask, Blueprint

from api.restplus import api


def create_app():
    flask_app = Flask(__name__)

    flask_app.secret_key = '12345'

    @flask_app.route('/')
    def homepage():
        return render_template('homepage.html')

    blueprint = Blueprint('api', __name__, url_prefix='/api')

    api.init_app(blueprint)

    # import this, so it gets initialized
    from api.endpoints.sentiment import ns
    assert ns.name == 'sentiment', ns.name

    flask_app.register_blueprint(blueprint)

    return flask_app


if __name__ == '__main__':
    with open('app_logging.json') as f:
        config.dictConfig(json.load(f)['logging'])

    app = create_app()

    log = logging.getLogger(__name__)
    log.debug('following endpoints are availabe')
    [log.debug(repr(p)) for p in app.url_map.iter_rules()]
    app.run(debug=True, ssl_context='adhoc')
