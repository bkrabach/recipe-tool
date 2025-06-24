"""Core authentication manager using Microsoft Entra ID device code flow."""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import msal

from .config import AuthConfig


@dataclass
class AuthResult:
    """Result of an authentication attempt."""

    success: bool
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


class AuthManager:
    """Manages Microsoft Entra ID authentication using device code flow."""

    def __init__(self, config: AuthConfig):
        """Initialize the auth manager.

        Args:
            config: Authentication configuration
        """
        self.config = config
        self._app: Optional[msal.PublicClientApplication] = None
        self._cache: Optional[msal.SerializableTokenCache] = None

    def _get_app(self) -> msal.PublicClientApplication:
        """Get or create the MSAL application instance."""
        if self._app is None:
            # Set up token cache
            self._cache = msal.SerializableTokenCache()

            # Load existing cache if it exists
            if self.config.cache_path and os.path.exists(self.config.cache_path):
                try:
                    with open(self.config.cache_path, "r") as f:
                        self._cache.deserialize(f.read())
                except Exception:
                    # If cache is corrupted, start fresh
                    pass

            # Create the MSAL application
            self._app = msal.PublicClientApplication(
                client_id=self.config.client_id, authority=self.config.authority, token_cache=self._cache
            )

        return self._app

    def _save_cache(self) -> None:
        """Save the token cache to disk."""
        if self._cache and self.config.cache_path and self._cache.has_state_changed:
            try:
                with open(self.config.cache_path, "w") as f:
                    f.write(self._cache.serialize())
            except Exception:
                # If we can't save cache, continue anyway
                pass

    async def authenticate(self) -> AuthResult:
        """Authenticate the user using device code flow.

        Returns:
            AuthResult with authentication status and token info
        """
        app = self._get_app()

        # First, try to get a token silently from cache
        accounts = app.get_accounts()
        if accounts:
            # Try to get token silently for the first account
            result = app.acquire_token_silent(self.config.scopes, account=accounts[0])
            if result and "access_token" in result:
                self._save_cache()
                expires_in = result.get("expires_in")
                if isinstance(expires_in, str):
                    expires_in = int(expires_in) if expires_in.isdigit() else None
                elif not isinstance(expires_in, int):
                    expires_in = None

                user_info = result.get("id_token_claims")
                if not isinstance(user_info, dict):
                    user_info = None

                return AuthResult(
                    success=True, access_token=result["access_token"], expires_in=expires_in, user_info=user_info
                )

        # No cached token available, initiate device code flow
        try:
            # Start the device code flow
            flow = app.initiate_device_flow(scopes=self.config.scopes)

            if "user_code" not in flow:
                return AuthResult(success=False, error="Failed to initiate device code flow")

            # Display the message to the user
            print(flow["message"])

            # Wait for the user to authenticate
            # This will block until the user completes authentication or it times out
            result = app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                self._save_cache()
                return AuthResult(
                    success=True,
                    access_token=result["access_token"],
                    expires_in=result.get("expires_in"),
                    user_info=result.get("id_token_claims"),
                )
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                return AuthResult(success=False, error=error_msg)

        except Exception as e:
            return AuthResult(success=False, error=str(e))

    async def get_access_token(self) -> Optional[str]:
        """Get a valid access token, refreshing if necessary.

        Returns:
            Access token string if available, None otherwise
        """
        app = self._get_app()

        accounts = app.get_accounts()
        if not accounts:
            return None

        # Try to get token silently
        result = app.acquire_token_silent(self.config.scopes, account=accounts[0])

        if result and "access_token" in result:
            self._save_cache()
            return result["access_token"]

        return None

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated.

        Returns:
            True if user has valid cached tokens, False otherwise
        """
        app = self._get_app()
        accounts = app.get_accounts()

        if not accounts:
            return False

        # Try to get token silently to check if it's valid
        result = app.acquire_token_silent(self.config.scopes, account=accounts[0])
        return result is not None and "access_token" in result

    async def logout(self) -> None:
        """Sign out the user and clear cached tokens."""
        app = self._get_app()
        accounts = app.get_accounts()

        # Remove all accounts from cache
        for account in accounts:
            app.remove_account(account)

        # Clear the cache file
        if self.config.cache_path and os.path.exists(self.config.cache_path):
            try:
                os.remove(self.config.cache_path)
            except Exception:
                pass

        # Reset the cache
        self._cache = None
        self._app = None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently authenticated user.

        Returns:
            User information dict if available, None otherwise
        """
        app = self._get_app()
        accounts = app.get_accounts()

        if accounts:
            return accounts[0]

        return None
