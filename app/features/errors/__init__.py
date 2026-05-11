from flask import abort

from app.engine import Feature

errors = Feature('errors', __name__, verbose_name='Errors')
errors.add_url_rule('/error/404', '404', view_func=lambda: abort(404))
errors.add_url_rule('/error/500', '500', view_func=lambda: abort(500))


@errors.on_load
def ready():
    """Import anything that should be initialized after the models here"""
    from . import handlers
