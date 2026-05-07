from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_seasurf import SeaSurf
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from app.database import Base

db = SQLAlchemy(model_class=Base, disable_autonaming=True)
migrate = Migrate()

# See configuration reference:
# https://flask-cors.readthedocs.io/en/latest/configuration.html#
cors = CORS()
csrf = SeaSurf()
talisman = Talisman()


def init_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)

    cors.init_app(app)
    csrf.init_app(app)
    talisman.init_app(app, content_security_policy=False)
