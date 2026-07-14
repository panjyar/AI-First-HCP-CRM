from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # All values must be set in the .env file — no hardcoded defaults.
    app_name: str
    app_env: str
    debug: bool
    api_prefix: str
    app_version: str

    # Comma-separated list of allowed frontend origins.
    # e.g. "http://localhost:5173,https://your-app.onrender.com"
    cors_origins: str

    groq_api_key: str
    groq_model: str

    database_url: str
    db_echo: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Parse the comma-separated CORS_ORIGINS into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
