"""Gradio components for Microsoft Entra ID authentication.

This module provides simple Gradio UI components for:
- Device code authentication flow
- Authentication status display
- User profile information
"""

from .auth_ui import AuthenticationUI, AuthStatus, create_auth_components

__all__ = [
    "AuthenticationUI",
    "AuthStatus",
    "create_auth_components",
]