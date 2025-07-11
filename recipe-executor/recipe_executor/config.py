# This file was generated by Codebase-Generator, do not edit directly
"""
Config component for the Recipe Executor.
Provides centralized, type-safe configuration via environment variables.
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RecipeExecutorConfig(BaseSettings):
    """
    Configuration for recipe executor API keys and credentials.

    This class automatically loads values from environment variables
    and .env files.
    """

    # Standard AI Provider API Keys
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY", description="API key for OpenAI")
    anthropic_api_key: Optional[str] = Field(
        default=None, alias="ANTHROPIC_API_KEY", description="API key for Anthropic"
    )

    # Azure OpenAI Credentials
    azure_openai_api_key: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_API_KEY", description="API key for Azure OpenAI"
    )
    azure_openai_base_url: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_BASE_URL", description="Base URL for Azure OpenAI endpoint"
    )
    azure_openai_api_version: str = Field(
        default="2025-03-01-preview", alias="AZURE_OPENAI_API_VERSION", description="API version for Azure OpenAI"
    )
    azure_openai_deployment_name: Optional[str] = Field(
        default=None, alias="AZURE_OPENAI_DEPLOYMENT_NAME", description="Deployment name for Azure OpenAI"
    )
    azure_use_managed_identity: bool = Field(
        default=False, alias="AZURE_USE_MANAGED_IDENTITY", description="Use Azure managed identity for authentication"
    )
    azure_client_id: Optional[str] = Field(
        default=None, alias="AZURE_CLIENT_ID", description="Client ID for Azure managed identity"
    )

    # Ollama Settings
    ollama_base_url: str = Field(
        default="http://localhost:11434", alias="OLLAMA_BASE_URL", description="Base URL for Ollama API"
    )

    model_config = SettingsConfigDict(
        env_prefix="RECIPE_EXECUTOR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Allow extra fields from .env file
    )


def load_configuration(recipe_env_vars: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    Args:
        recipe_env_vars: Optional list of additional environment variable names
                         that the recipe requires. These will be loaded and added
                         to the configuration with lowercase keys.

    Returns:
        Dictionary containing all configuration values, with None values excluded.
    """
    # Load standard settings
    settings = RecipeExecutorConfig()
    # Convert to dict, excluding None values
    config: Dict[str, Any] = settings.model_dump(exclude_none=True)

    # Load recipe-specific variables
    if recipe_env_vars:
        for var_name in recipe_env_vars:
            value = os.getenv(var_name)
            if value is not None:
                # Key names are lowercase for consistency
                key = var_name.lower()
                config[key] = value

    return config
