import os

from dotenv import load_dotenv
from flask import Flask

from app.healthcheck import init_healthcheck

load_dotenv()


def create_app(settings_module: str = ''):
    app = Flask(__name__)

    try:
        settings = settings_module or os.environ.get('FLASK_SETTINGS_MODULE')
        app.config.from_object(settings)
    except ImportError as e:
        raise RuntimeError('FLASK_SETTINGS_MODULE was set improperly') from e

    init_healthcheck(app)

    return app
