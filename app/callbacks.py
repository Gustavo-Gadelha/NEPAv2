from flask import request

from app.extensions import csrf


@csrf.disable_cookie
def disable_cookie(response):
    return 'session' not in request.cookies
