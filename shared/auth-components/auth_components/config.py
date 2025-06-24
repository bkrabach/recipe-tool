"""Configuration management for Microsoft Entra ID authentication."""

import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv


@dataclass
class AuthConfig:
    """Configuration for Microsoft Entra ID authentication."""

    client_id: str
    tenant_id: str
    scopes: List[str]
    authority: Optional[str] = None
    cache_path: Optional[str] = None

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "AuthConfig":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file to load

        Returns:
            AuthConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from .env in current directory

        client_id = os.getenv("ENTRA_CLIENT_ID")
        tenant_id = os.getenv("ENTRA_TENANT_ID")

        if not client_id:
            raise ValueError("ENTRA_CLIENT_ID environment variable is required")
        if not tenant_id:
            raise ValueError("ENTRA_TENANT_ID environment variable is required")

        # Default scopes optimized for personal OneDrive access
        scopes_str = os.getenv("ENTRA_SCOPES", "User.Read,Files.ReadWrite.All")
        scopes = [s.strip() for s in scopes_str.split(",")]

        # Authority URL - default to common if not specified
        authority = os.getenv("ENTRA_AUTHORITY")
        if not authority:
            authority = f"https://login.microsoftonline.com/{tenant_id}"

        # Cache path - default to .auth_cache in current directory
        cache_path = os.getenv("TOKEN_CACHE_PATH", ".auth_cache")

        return cls(client_id=client_id, tenant_id=tenant_id, scopes=scopes, authority=authority, cache_path=cache_path)
