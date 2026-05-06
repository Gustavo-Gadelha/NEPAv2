import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import init_extensions
from app.healthcheck import register_healthcheck

load_dotenv()


def create_app(settings_module: str = ''):
    app = Flask(__name__)

    try:
        settings = settings_module or os.environ.get('FLASK_SETTINGS_MODULE')
        app.config.from_object(settings)
    except ImportError as e:
        raise RuntimeError('FLASK_SETTINGS_MODULE was set improperly') from e

    init_extensions(app)
    register_healthcheck(app)

    return app
