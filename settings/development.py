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

CORS_ORIGINS = env.list('CORS_ORIGINS')
CORS_RESOURCES = env.str('CORS_RESOURCES')
CORS_SUPPORTS_CREDENTIALS = env.bool('CORS_SUPPORTS_CREDENTIALS', default=True)
CORS_ALLOW_HEADERS = env.list('CORS_ALLOW_HEADERS', default='*')
CORS_EXPOSE_HEADERS = env.list('CORS_EXPOSE_HEADERS', default=None)
