import logging

import sentry_sdk
from environs import env
from sentry_sdk.integrations.flask import FlaskIntegration

logger = logging.getLogger(__name__)


def init_sentry():
    dsn = env.str('SENTRY_DSN', default=None)

    if not dsn:
        logger.info('SENTRY_DSN is not set, Sentry will not be initialized.')
        return

    traces_sample_rate = env.float('SENTRY_TRACE_SAMPLE_RATES', default=0.1)

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
