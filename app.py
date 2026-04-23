import os
import sys
import logging

from dotenv import load_dotenv

revision = os.getenv('REVISION', 'master')
env_path = os.getenv('APP_SETTINGS', f'env.{revision}')
try:
    log_level = os.getenv('LOG_LEVEL', "INFO")
    def_format = "[%(asctime)s] [%(process)d] [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s"
    format = os.getenv('LOG_FORMAT', def_format)
    logging.basicConfig(level=log_level, format=format)
    logging.info(f"Set LOG Level: '{log_level}'")
    load_dotenv(verbose=True, dotenv_path=env_path)
except Exception as e:
    print(f"Failed to load dot env: {e}")
    sys.exit(-1)

from flask import Flask
from api import api


logger = logging.getLogger(__name__)


def prefix_route(route_function, prefix='', mask='{0}{1}'):
    def newroute(route, *args, **kwargs):
        '''New function to prefix the route'''
        return route_function(mask.format(prefix, route), *args, **kwargs)

    return newroute


context_path = os.getenv('CONTEXT_PATH')
app = Flask(__name__, static_url_path=f"{context_path}/static")
app.config['SESSION_COOKIE_NAME'] = context_path[1:]
app.route = prefix_route(app.route, context_path)
app.register_blueprint(api.api, url_prefix=context_path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))