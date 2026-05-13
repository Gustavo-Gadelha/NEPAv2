from app.engine import Feature

auth = Feature('auth', __name__, verbose_name='Auth', url_prefix='/auth')


@auth.on_load
def ready():
    """Import anything that should be initialized after the models here"""
