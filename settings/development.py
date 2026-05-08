from environs import env

DEBUG = True
ENV = 'development'

SECRET_KEY = env.str('SECRET_KEY', default='dev-secret-key')
SECRET_KEY_FALLBACKS = env.list('SECRET_KEY_FALLBACKS', default=[])

SERVER_NAME = env.str('SERVER_NAME', default=None)
TRUSTED_HOSTS = env.list('TRUSTED_HOSTS', default=None)

MAX_CONTENT_LENGTH = env.int('MAX_CONTENT_LENGTH', default=16 * 1024 * 1024)  # 16MB

SQLALCHEMY_DATABASE_URI = env.str('SQLALCHEMY_DATABASE_URI', default='sqlite:///sqlite3.db')
SQLALCHEMY_ECHO = env.bool('SQLALCHEMY_ECHO', default=True)
SQLALCHEMY_RECORD_QUERIES = env.bool('SQLALCHEMY_RECORD_QUERIES', default=False)
SQLALCHEMY_TRACK_MODIFICATIONS = env.bool('SQLALCHEMY_TRACK_MODIFICATIONS', default=False)

MAIL_SERVER = env.str('MAIL_SERVER', default='localhost')
MAIL_PORT = env.int('MAIL_PORT', default=25)
MAIL_USERNAME = env.str('MAIL_USERNAME', default=None)
MAIL_PASSWORD = env.str('MAIL_PASSWORD', default=None)

MAIL_USE_TLS = env.bool('MAIL_USE_TLS', default=False)
MAIL_USE_SSL = env.bool('MAIL_USE_SSL', default=False)

MAIL_DEFAULT_SENDER = env.str('MAIL_DEFAULT_SENDER', default='noreply@localhost')

CORS_ORIGINS = env.list('CORS_ORIGINS')
CORS_RESOURCES = env.str('CORS_RESOURCES')
CORS_SUPPORTS_CREDENTIALS = env.bool('CORS_SUPPORTS_CREDENTIALS', default=True)
CORS_ALLOW_HEADERS = env.list('CORS_ALLOW_HEADERS', default='*')
CORS_EXPOSE_HEADERS = env.list('CORS_EXPOSE_HEADERS', default=None)

RATELIMIT_ENABLED = env.bool('RATELIMIT_ENABLED', default=True)
RATELIMIT_STORAGE_URI = env.str('RATELIMIT_STORAGE_URI', default='memory://')
RATELIMIT_STRATEGY = env.str('RATELIMIT_STRATEGY', default='fixed-window')
RATELIMIT_HEADERS_ENABLED = env.bool('RATELIMIT_HEADERS_ENABLED', default=True)
RATELIMIT_DEFAULT = env.list('RATELIMIT_DEFAULT', default='3000 per day,300 per hour,30 per minute')
