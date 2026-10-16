"""Environment-backed application configuration."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with secure, local-development defaults."""

    app_env: str = "development"
    database_url: str = "sqlite:///./data/students.db"
    max_request_size_bytes: int = Field(default=1_048_576, ge=1_024, le=10_485_760)
    cors_allowed_origins: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        """Return an explicit allow-list; an empty value disables CORS."""
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
