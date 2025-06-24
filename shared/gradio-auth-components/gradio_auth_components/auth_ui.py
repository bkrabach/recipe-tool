"""Gradio UI components for Microsoft Entra ID authentication."""

import gradio as gr
import asyncio
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# This will be imported when used in actual apps
# from auth_components import AuthManager, AuthConfig


@dataclass
class AuthStatus:
    """Authentication status information."""
    is_authenticated: bool
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AuthenticationUI:
    """Gradio UI component for Microsoft Entra ID authentication."""
    
    def __init__(self, auth_config=None):
        """Initialize authentication UI component."""
        self.auth_config = auth_config
        self.auth_manager = None
        self._current_status = AuthStatus(is_authenticated=False)
        
        # Will be set when auth_components is available
        if auth_config:
            try:
                from auth_components import AuthManager
                self.auth_manager = AuthManager(auth_config)
            except ImportError:
                pass
    
    def create_auth_interface(self) -> gr.Blocks:
        """Create the complete authentication interface."""
        with gr.Blocks(title="Microsoft Authentication") as auth_interface:
            gr.Markdown("# 🔐 Microsoft Authentication")
            
            # Status display
            with gr.Row():
                with gr.Column(scale=2):
                    status_display = gr.Markdown(
                        self._format_status_message(self._current_status),
                        elem_id="auth_status"
                    )
                    
                with gr.Column(scale=1):
                    refresh_btn = gr.Button("🔄 Check Status", size="sm")
            
            # Authentication section
            gr.Markdown("## Authentication")
            
            with gr.Row():
                auth_btn = gr.Button("🚀 Start Authentication", variant="primary")
                logout_btn = gr.Button("🚪 Logout", variant="secondary")
            
            # Device code display (initially hidden)
            device_code_display = gr.Markdown(visible=False, elem_id="device_code")
            
            # Progress indicator
            auth_progress = gr.HTML(visible=False, elem_id="auth_progress")
            
            # User info display
            with gr.Row():
                with gr.Column():
                    user_info_display = gr.JSON(
                        label="User Information",
                        visible=False,
                        elem_id="user_info"
                    )
            
            # Event handlers
            auth_btn.click(
                fn=self._start_authentication,
                outputs=[device_code_display, auth_progress, status_display]
            )
            
            refresh_btn.click(
                fn=self._check_auth_status,
                outputs=[status_display, user_info_display]
            )
            
            logout_btn.click(
                fn=self._logout,
                outputs=[status_display, user_info_display, device_code_display]
            )
            
            # Auto-check status on load
            auth_interface.load(
                fn=self._check_auth_status,
                outputs=[status_display, user_info_display]
            )
        
        return auth_interface
    
    def create_simple_auth_button(self) -> Tuple[gr.Button, gr.Markdown]:
        """Create a simple authentication button and status display."""
        auth_btn = gr.Button("🔐 Authenticate with Microsoft", variant="primary")
        status_md = gr.Markdown(self._format_status_message(self._current_status))
        
        auth_btn.click(
            fn=self._quick_auth,
            outputs=[status_md]
        )
        
        return auth_btn, status_md
    
    def _format_status_message(self, status: AuthStatus) -> str:
        """Format authentication status as markdown."""
        if status.error_message:
            return f"❌ **Error**: {status.error_message}"
        
        if status.is_authenticated:
            user_info = f"**{status.user_name}**" if status.user_name else "Unknown User"
            if status.user_email:
                user_info += f" ({status.user_email})"
            
            expires_info = ""
            if status.expires_at:
                expires_info = f"\n*Token expires: {status.expires_at.strftime('%Y-%m-%d %H:%M')}*"
            
            return f"✅ **Authenticated** as {user_info}{expires_info}"
        
        return "❌ **Not Authenticated** - Please sign in to continue"
    
    def _start_authentication(self) -> Tuple[gr.Markdown, gr.HTML, gr.Markdown]:
        """Start the authentication process."""
        if not self.auth_manager:
            error_status = AuthStatus(
                is_authenticated=False,
                error_message="Authentication not configured"
            )
            return (
                gr.Markdown(visible=False),
                gr.HTML(visible=False),
                gr.Markdown(self._format_status_message(error_status))
            )
        
        try:
            # This would normally start the device flow
            # For now, return mock UI elements
            device_code_html = """
            <div style="padding: 20px; border: 2px solid #007acc; border-radius: 8px; background: #f0f8ff;">
                <h3>🔑 Device Code Authentication</h3>
                <p><strong>Step 1:</strong> Go to <a href="https://microsoft.com/devicelogin" target="_blank">microsoft.com/devicelogin</a></p>
                <p><strong>Step 2:</strong> Enter this code: <code style="font-size: 18px; font-weight: bold;">ABC123DEF</code></p>
                <p><strong>Step 3:</strong> Complete authentication in the browser</p>
            </div>
            """
            
            progress_html = """
            <div style="text-align: center; padding: 10px;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto;"></div>
                <p style="margin-top: 10px;"><em>Waiting for authentication...</em></p>
            </div>
            <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
            </style>
            """
            
            return (
                gr.Markdown(device_code_html, visible=True),
                gr.HTML(progress_html, visible=True),
                gr.Markdown("🔄 **Authentication in progress...**")
            )
        
        except Exception as e:
            error_status = AuthStatus(
                is_authenticated=False,
                error_message=f"Authentication failed: {str(e)}"
            )
            return (
                gr.Markdown(visible=False),
                gr.HTML(visible=False),
                gr.Markdown(self._format_status_message(error_status))
            )
    
    def _check_auth_status(self) -> Tuple[gr.Markdown, gr.JSON]:
        """Check current authentication status."""
        if not self.auth_manager:
            status = AuthStatus(
                is_authenticated=False,
                error_message="Authentication manager not configured"
            )
            return (
                gr.Markdown(self._format_status_message(status)),
                gr.JSON(visible=False)
            )
        
        try:
            # Check if authenticated
            is_auth = self.auth_manager.is_authenticated()
            
            if is_auth:
                user_info = self.auth_manager.get_user_info()
                status = AuthStatus(
                    is_authenticated=True,
                    user_name=user_info.get('name') if user_info else None,
                    user_email=user_info.get('username') if user_info else None
                )
                
                user_data = user_info if user_info else {"status": "authenticated"}
                return (
                    gr.Markdown(self._format_status_message(status)),
                    gr.JSON(user_data, visible=True)
                )
            else:
                status = AuthStatus(is_authenticated=False)
                return (
                    gr.Markdown(self._format_status_message(status)),
                    gr.JSON(visible=False)
                )
        
        except Exception as e:
            status = AuthStatus(
                is_authenticated=False,
                error_message=f"Status check failed: {str(e)}"
            )
            return (
                gr.Markdown(self._format_status_message(status)),
                gr.JSON(visible=False)
            )
    
    def _logout(self) -> Tuple[gr.Markdown, gr.JSON, gr.Markdown]:
        """Logout and clear authentication."""
        try:
            # Clear any cached tokens
            if self.auth_manager:
                # This would clear the token cache
                pass
            
            self._current_status = AuthStatus(is_authenticated=False)
            
            return (
                gr.Markdown(self._format_status_message(self._current_status)),
                gr.JSON(visible=False),
                gr.Markdown(visible=False)
            )
        
        except Exception as e:
            status = AuthStatus(
                is_authenticated=False,
                error_message=f"Logout failed: {str(e)}"
            )
            return (
                gr.Markdown(self._format_status_message(status)),
                gr.JSON(visible=False),
                gr.Markdown(visible=False)
            )
    
    def _quick_auth(self) -> gr.Markdown:
        """Quick authentication for simple button interface."""
        try:
            if not self.auth_manager:
                status = AuthStatus(
                    is_authenticated=False,
                    error_message="Please configure authentication first"
                )
                return gr.Markdown(self._format_status_message(status))
            
            # Check if already authenticated
            if self.auth_manager.is_authenticated():
                user_info = self.auth_manager.get_user_info()
                status = AuthStatus(
                    is_authenticated=True,
                    user_name=user_info.get('name') if user_info else None,
                    user_email=user_info.get('username') if user_info else None
                )
            else:
                status = AuthStatus(
                    is_authenticated=False,
                    error_message="Authentication required - please use the full auth interface"
                )
            
            return gr.Markdown(self._format_status_message(status))
        
        except Exception as e:
            status = AuthStatus(
                is_authenticated=False,
                error_message=f"Quick auth failed: {str(e)}"
            )
            return gr.Markdown(self._format_status_message(status))


def create_auth_components(auth_config=None) -> Tuple[gr.Blocks, AuthenticationUI]:
    """Helper function to create authentication components."""
    auth_ui = AuthenticationUI(auth_config)
    interface = auth_ui.create_auth_interface()
    return interface, auth_ui