from datetime import UTC, datetime

from flask import current_app, jsonify, request
from slugify import slugify
from werkzeug.exceptions import HTTPException

from . import errors


def handle_response(slug: str, message: str | None, status_code: int):
    body = {
        'error': slug,
        'message': message,
        'status_code': status_code,
        'timestamp': datetime.now(UTC).isoformat(),
        'path': request.path,
    }

    return jsonify(body), status_code


@errors.app_errorhandler(HTTPException)
def handle_http_exception(error: HTTPException):
    if not error.code or error.code >= 500:
        current_app.logger.exception(error)
    else:
        current_app.logger.debug('API error %d on %s: %s', error.code, request.path, error)

    slug = slugify(error.name, separator='_')
    return handle_response(slug, error.description, error.code or 500)


@errors.app_errorhandler(Exception)
def handle_unexpected(error: Exception):
    current_app.logger.exception(error)
    return handle_response('internal_server_error', 'An unexpected error occurred.', 500)
