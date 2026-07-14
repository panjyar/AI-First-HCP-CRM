from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-First HCP CRM API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"
    frontend_url: str = "http://localhost:5173"

    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/hcp_crm"
    )
    db_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
