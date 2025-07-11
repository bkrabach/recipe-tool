"""Configuration settings for the Document Generator app."""

import os
from typing import NamedTuple, List


class ExampleOutline(NamedTuple):
    """Configuration for an example document outline."""

    name: str
    path: str


class Settings:
    """Configuration settings for the Document Generator app."""

    # App settings
    app_title: str = "Document Generator"
    app_description: str = "Create structured documents with AI assistance"

    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # "openai" or "azure"
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o")

    @property
    def model_id(self) -> str:
        """Get the full model ID for recipe-executor."""
        return f"{self.llm_provider}/{self.default_model}"

    # Example outlines
    example_outlines: List[ExampleOutline] = [
        ExampleOutline(
            name="README Generator",
            path="examples/readme.docpack",
        ),
        ExampleOutline(
            name="Product Launch Documentation",
            path="examples/launch-documentation.docpack",
        ),
    ]

    # Theme settings
    theme: str = "soft"  # Use "default", "soft", "glass", etc.


# Create global settings instance
settings = Settings()
