from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_migrate import Migrate
from flask_seasurf import SeaSurf
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from app.database import Base
from app.engine import FeatureRegistry

db = SQLAlchemy(model_class=Base, disable_autonaming=True)
migrate = Migrate()
registry = FeatureRegistry()

cors = CORS()
csrf = SeaSurf()
talisman = Talisman()

mail = Mail()
limiter = Limiter(get_remote_address)


def init_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    registry.init_app(app)

    cors.init_app(app)
    csrf.init_app(app)
    talisman.init_app(app, content_security_policy=False)

    mail.init_app(app)
    limiter.init_app(app)
