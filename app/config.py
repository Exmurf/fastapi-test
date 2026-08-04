from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    app_name:str = "Product CRUD API"
    database_url:str
    debug:bool = False

    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding= "utf-8",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()