from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Product CRUD API"
    database_url: str
    redis_url: str
    debug: bool = False

    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    refresh_token_expire_days: int = 30

    product_cache_ttl_seconds: int = 300

    login_limit: int = 5
    login_window_seconds: int = 60

    register_limit: int = 3
    register_window_seconds: int = 600

    product_read_limit: int = 100
    product_read_window_seconds: int = 60

    product_write_limit: int = 30
    product_write_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()