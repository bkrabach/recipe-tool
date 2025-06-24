"""Microsoft Entra ID authentication components."""

from .auth_manager import AuthManager, AuthResult
from .config import AuthConfig

__all__ = ["AuthManager", "AuthResult", "AuthConfig"]