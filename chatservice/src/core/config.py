import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    ENV: str = os.environ.get("ENV", "local")
    APP_NAME: str = os.environ.get("APP_NAME", "fastapi-chatservice")
    DEBUG: bool = os.environ.get("DEBUG", True)
    APP_HOST: str = os.environ.get("HOST", "0.0.0.0")
    APP_PORT: int = os.environ.get("PORT", 8000)
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)


config = Config()
