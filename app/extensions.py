from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.database import Base

db = SQLAlchemy(model_class=Base, disable_autonaming=True)


def init_extensions(app: Flask):
    db.init_app(app)
