from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.database import Base

db = SQLAlchemy(model_class=Base, disable_autonaming=True)
migrate = Migrate()


def init_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
