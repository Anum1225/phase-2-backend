"""
Configuration management for Task API Backend.

Loads environment variables and provides typed configuration objects.
All secrets must be provided via environment variables (never hardcoded).
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        """Initialize settings from environment variables."""
        # Database Configuration
        self.DATABASE_URL: str = self._get_required_env("DATABASE_URL")

        # Authentication Configuration
        self.BETTER_AUTH_SECRET: str = self._get_required_env("BETTER_AUTH_SECRET")

        # CORS Configuration
        # Default includes localhost for development and common Vercel/production URLs
        default_cors = "http://localhost:3000,http://localhost:5173,https://hackathon-2-iota-three.vercel.app"
        cors_origins_str = os.getenv("CORS_ORIGINS", default_cors)
        self.CORS_ORIGINS: List[str] = [
            origin.strip() for origin in cors_origins_str.split(",") if origin.strip()
        ]

        # JWT Configuration
        self.JWT_ALGORITHM: str = "HS256"
        self.JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

        # Server Configuration
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = int(os.getenv("PORT", "8000"))

        # Validate configuration
        self._validate()

    def _get_required_env(self, key: str) -> str:
        """
        Get required environment variable or raise error.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable {key} is not set. "
                f"Please set it in .env file or environment."
            )
        return value

    def _validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ValueError: If any configuration value is invalid
        """
        # Validate DATABASE_URL format
        if not self.DATABASE_URL.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql://' or 'postgres://'"
            )

        # Validate JWT secret length (minimum 32 characters for security)
        if len(self.BETTER_AUTH_SECRET) < 32:
            raise ValueError(
                "BETTER_AUTH_SECRET must be at least 32 characters long for security"
            )

        # Validate CORS origins format
        if not self.CORS_ORIGINS:
            raise ValueError("CORS_ORIGINS must contain at least one origin")


# Global settings instance
settings = Settings()
