import json
import os
from logging import config, getLogger

from sentiment.web import create_app

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
        app.run(host='0.0.0.0', port=os.getenv('PORT', 5000), ssl_context='adhoc')
