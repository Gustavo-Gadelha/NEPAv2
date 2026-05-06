from flask import Flask
from healthcheck import EnvironmentDump, HealthCheck

health = HealthCheck()
envdump = EnvironmentDump(include_process=False)


def init_healthcheck(app: Flask):
    app.add_url_rule('/healthcheck', 'healthcheck', view_func=lambda: health.run())
    app.add_url_rule('/environment', 'environment', view_func=lambda: envdump.run())
