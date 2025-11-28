"""Application configuration module.

This module provides centralized configuration management using pydantic-settings.
Settings are loaded from environment variables and .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.shared.enums import Environment


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        environment: Current runtime environment. Defaults to development.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT

    @property
    def debug(self) -> bool:
        """Check if application is running in debug mode.

        Returns:
            True if environment is development, testing, or staging.
        """
        return self.environment in (
            Environment.DEVELOPMENT,
            Environment.TESTING,
            Environment.STAGING,
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings instance.

    Uses lru_cache to ensure settings are loaded only once.

    Returns:
        Singleton Settings instance.
    """
    return Settings()
