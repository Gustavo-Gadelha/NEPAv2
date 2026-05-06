from environs import env

DEBUG = True
ENV = 'development'

SECRET_KEY = env.str('SECRET_KEY', default='dev-secret-key')
SECRET_KEY_FALLBACKS = env.list('SECRET_KEY_FALLBACKS', default=[])

SERVER_NAME = env.str('SERVER_NAME', default=None)
TRUSTED_HOSTS = env.list('TRUSTED_HOSTS', default=['*'])

MAX_CONTENT_LENGTH = env.int('MAX_CONTENT_LENGTH', default=16 * 1024 * 1024)  # 16MB

SQLALCHEMY_DATABASE_URI = env.str('SQLALCHEMY_DATABASE_URI', default='sqlite:///sqlite3.db')

LOG_LEVEL = 'DEBUG'
