"""
Configuration Management Module

Handles secure loading and validation of environment variables with support
for local .env files and cloud deployment with GCP Secret Manager integration.
"""
# Import libraries
import os
import sys
import logging
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import SecretStr, Field, ValidationError


class LogLevel(str, Enum):
    """Standard logging levels for application logging configuration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class SystemConfig(BaseSettings):
    """
    Main application configuration with environment-based loading.

    Supports local development with .env files and cloud deployment
    with environment variables from GCP Secret Manager.

    Read .env.example for more information about Environment Variables
    """

    # Application configurations
    app_name: str = Field(
        default="crypto-news-pipeline",
        description="Application identifier"
    )
    app_description: str = Field(
        default="A LangGraph workflow that fetches crypto news, performs sentiment analysis, and sends notifications",
        description="Application description"
    )
    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    environment: str = Field(
        default="development",
        description="Deployment environment"
    )
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )

    # Database configurations
    db_uri: SecretStr = Field(
        description="Database connection URI"
    )
    db_name: str = Field(
        ...,
        description="Database name"
    )

    # LLM configurations
    model_name: str = Field(
        default="gpt-4o",
        description="Large Language Model name"
    )
    model_api_key: SecretStr = Field(
        ...,
        description="Large Language Model API key"
    )

    # Telegram configurations
    bot_token: SecretStr = Field(
        ...,
        description="Telegram bot token"
    )
    group_id: SecretStr = Field(
        ...,
        description="Private group id"
    )

    # Crypto news configurations
    news_api_key: SecretStr = Field(
        ...,
        description="News API key"
    )
    news_url: str = Field(
        ...,
        description="News API URL"
    )

    # LangSmith configurations
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangSmith tracing v2"
    )
    langsmith_api_key: SecretStr = Field(
        ...,
        description="LangSmith API key"
    )
    langsmith_project: str = Field(
        default="crypto-news-pipeline",
        description="LangSmith project name"
    )


    def is_production(self) -> bool:
        """Check if running in a production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in a development environment."""
        return self.environment.lower() == "development"

    class Config:
        """Pydantic configuration for environment variable loading."""
        env_file = Path(__file__).parent.parent.parent / '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_nested_delimiter = '__'
        extra = 'forbid'
        validate_default = True


# Initialize logging with basic configuration
from src.config.logging_config import setup_logging
setup_logging()

# Load and validate configuration on module import
try:
    config = SystemConfig()
    logging.info(f"Configuration loaded for {config.environment.upper()} environment.")
except ValidationError as e:
    logging.error(f"Configuration validation failed: {e}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    sys.exit(1)


# Public API
__all__ = ['config', 'SystemConfig']
