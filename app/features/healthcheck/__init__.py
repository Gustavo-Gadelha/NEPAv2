from app.engine import Feature
from healthcheck import EnvironmentDump, HealthCheck

from .checks import database_available
from .environment import installed_features

health = HealthCheck()
health.add_check(database_available)

envdump = EnvironmentDump(include_process=False)
envdump.add_section('installed_features', installed_features)

healthcheck = Feature('healthcheck', __name__, verbose_name='Healthcheck')
healthcheck.add_url_rule('/healthcheck', 'healthcheck', view_func=lambda: health.run())
healthcheck.add_url_rule('/environment', 'environment', view_func=lambda: envdump.run())


@healthcheck.on_load
def ready():
    """Import anything that should be initialized after the models here"""
