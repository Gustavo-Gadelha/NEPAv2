from dotenv import load_dotenv
from flask import Flask

from app.conf import Config, get_settings
from app.extensions import init_extensions
from app.sentry import init_sentry

load_dotenv()


def create_app(override_settings: Config | None = None):
    app = Flask(__name__)

    try:
        settings = override_settings or get_settings()
        app.config.from_mapping(settings.model_dump())
    except ImportError as e:
        raise RuntimeError('FLASK_SETTINGS_MODULE was set improperly') from e

    init_extensions(app)
    init_sentry(app)

    from app.extensions import registry

    for feature in registry.get_features():
        app.register_blueprint(feature)

    return app
