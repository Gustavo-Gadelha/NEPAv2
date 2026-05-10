import logging

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

logger = logging.getLogger(__name__)


def init_sentry(app: Flask):
    dsn = app.config.get('SENTRY_DSN')

    if not dsn:
        logger.info('SENTRY_DSN is not set, Sentry will not be initialized.')
        return

    traces_sample_rate = app.config.get('SENTRY_TRACE_SAMPLE_RATES')

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FlaskIntegration(),
        ],
        # Add data like request headers and IP for users, if applicable;
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=traces_sample_rate,
    )
