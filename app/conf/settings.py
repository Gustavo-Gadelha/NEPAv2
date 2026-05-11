import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        extra='allow',
        case_sensitive=True,
    )

    ENV: Literal['development', 'production'] = 'development'
    DEBUG: bool = False
    TESTING: bool = False

    REDIS_URL: str

    INSTALLED_FEATURES: list[str] = [
        'app.features.healthcheck',
    ]

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    APP_DIR: Path = BASE_DIR / 'app'
    UPLOAD_DIR: Path = BASE_DIR / 'uploads'
    INSTANCE_DIR: Path = BASE_DIR / 'instance'
    STATIC_DIR: Path = BASE_DIR / 'static'
    TEMPLATES_DIR: Path = BASE_DIR / 'templates'

    UPLOAD_ALLOWED_EXTENSIONS: set[str] = {
        'jpg',
        'jpeg',
        'png',
        'gif',
        'pdf',
    }

    SECRET_KEY: str
    SECRET_KEY_FALLBACKS: list[str] = []

    SERVER_NAME: str | None = None
    TRUSTED_HOSTS: list[str] | None = None

    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB

    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_ECHO: bool = False
    SQLALCHEMY_RECORD_QUERIES: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    MAIL_SERVER: str = 'localhost'
    MAIL_PORT: int = 25
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None

    MAIL_USE_TLS: bool = False
    MAIL_USE_SSL: bool = False

    MAIL_DEFAULT_SENDER: str = 'noreply@localhost'

    SESSION_COOKIE_SECURE: bool = False
    PREFERRED_URL_SCHEME: str = 'http'

    CORS_ORIGINS: list[str] | str = []
    CORS_RESOURCES: str = r'/*'
    CORS_SUPPORTS_CREDENTIALS: bool = True
    CORS_ALLOW_HEADERS: list[str] | str = '*'
    CORS_EXPOSE_HEADERS: list[str] | None = None

    RATELIMIT_ENABLED: bool = True
    RATELIMIT_STORAGE_URI: str = 'memory://'
    RATELIMIT_STRATEGY: str = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED: bool = True
    RATELIMIT_DEFAULT: str = '3000 per day,300 per hour,30 per minute'

    SENTRY_DSN: str | None = None
    SENTRY_TRACE_SAMPLE_RATES: float = 0.1

    def ensure_dirs(self) -> None:
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        self.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    ENV: Literal['development'] = 'development'
    DEBUG: bool = True

    REDIS_URL: str = 'redis://localhost:6379'

    SECRET_KEY: str = 'unsafe-secret-key'

    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///sqlite3.db'
    SQLALCHEMY_ECHO: bool = True

    TRUSTED_HOSTS: list[str] | None = None


class ProductionConfig(Config):
    ENV: Literal['production'] = 'production'
    DEBUG: bool = False

    REDIS_URL: str = 'redis://redis:6379'

    SESSION_COOKIE_SECURE: bool = True
    PREFERRED_URL_SCHEME: str = 'https'

    RATELIMIT_STORAGE_URI: str = REDIS_URL

    SQLALCHEMY_DATABASE_URI: str
    SECRET_KET: str


def get_settings(**kwargs) -> Config:
    env = os.getenv('ENV', 'development')
    match env:
        case 'production':
            _settings = ProductionConfig(**kwargs)
        case 'development':
            _settings = DevelopmentConfig(**kwargs)
        case _:
            raise RuntimeError(f'Invalid environment setting: {env!r}')

    _settings.ensure_dirs()
    return _settings
