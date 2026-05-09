from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    database_url: str = "postgresql://postgres:postgres@localhost:5432/smartapply"
    anthropic_api_key: str = ""
    app_env : str = "development"
    log_level: str = 'INFO'
    analyze_rate_limit: int = 10
    analyze_rate_limit_window: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()