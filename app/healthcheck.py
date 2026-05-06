from flask import Flask
from healthcheck import EnvironmentDump, HealthCheck

from app.extensions import db

health = HealthCheck()
envdump = EnvironmentDump(include_process=False)


def database_available():
    db.session.execute(db.text('SELECT 1'))
    return True, 'database ok'


health.add_check(database_available)


def register_healthcheck(app: Flask):
    app.add_url_rule('/healthcheck', 'healthcheck', view_func=lambda: health.run())
    app.add_url_rule('/environment', 'environment', view_func=lambda: envdump.run())
