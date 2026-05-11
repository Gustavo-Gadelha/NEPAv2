from flask import abort

from app.engine import Feature

errors = Feature('errors', __name__, verbose_name='Errors')


@errors.on_load
def ready():
    """Import anything that should be initialized after the models here"""
    from . import handlers
