import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.extensions import init_extensions
from app.healthcheck import register_healthcheck
from app.sentry import init_sentry

load_dotenv()


def create_app(settings_module: str = ''):
    app = Flask(__name__)

    try:
        settings = settings_module or os.environ.get('FLASK_SETTINGS_MODULE')
        app.config.from_object(settings)
    except ImportError as e:
        raise RuntimeError('FLASK_SETTINGS_MODULE was set improperly') from e

    # See configuration reference:
    # https://flask-cors.readthedocs.io/en/latest/configuration.html#
    CORS(app)

    init_extensions(app)
    register_healthcheck(app)

    init_sentry()

    return app
