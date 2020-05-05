from flask import render_template, Flask, Blueprint

from api.restplus import api


def create_app():
    flask_app = Flask(__name__)

    flask_app.secret_key = '12345'

    blueprint = Blueprint('api', __name__, url_prefix='/api')

    api.init_app(blueprint)
    flask_app.register_blueprint(blueprint)

    return flask_app


if __name__ == '__main__':
    app = create_app()


    @app.route('/')
    def homepage():
        html = render_template('homepage.html')
        return html


    print([p for p in app.url_map.iter_rules()])
    app.run(debug=True, ssl_context='adhoc')
