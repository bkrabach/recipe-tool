#!/usr/bin/env python3
"""Simple test script for Microsoft Entra ID authentication."""

import asyncio
import sys
import os

# Add the current directory to Python path so we can import auth_components
sys.path.insert(0, os.path.dirname(__file__))

from auth_components import AuthManager, AuthConfig


async def test_authentication():
    """Test the authentication flow."""
    print("🔐 Testing Microsoft Entra ID Authentication")
    print("=" * 50)
    
    try:
        # Load configuration from environment
        print("📋 Loading configuration from environment variables...")
        config = AuthConfig.from_env()
        print(f"✅ Client ID: {config.client_id[:8]}...")
        print(f"✅ Tenant ID: {config.tenant_id}")
        print(f"✅ Authority: {config.authority}")
        print(f"✅ Scopes: {', '.join(config.scopes)}")
        print()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nRequired environment variables:")
        print("  ENTRA_CLIENT_ID=your-client-id")
        print("  ENTRA_TENANT_ID=your-tenant-id")
        print("\nOptional environment variables:")
        print("  ENTRA_AUTHORITY=https://login.microsoftonline.com/{tenant-id}")
        print("  ENTRA_SCOPES=https://graph.microsoft.com/.default")
        print("  TOKEN_CACHE_PATH=.auth_cache")
        return False
    
    # Create auth manager
    auth_manager = AuthManager(config)
    
    # Check if already authenticated
    print("🔍 Checking existing authentication...")
    if auth_manager.is_authenticated():
        print("✅ Already authenticated!")
        
        # Get user info
        user_info = auth_manager.get_user_info()
        if user_info:
            print(f"👤 User: {user_info.get('username', 'Unknown')}")
        
        # Test getting access token
        token = await auth_manager.get_access_token()
        if token:
            print(f"🔑 Access token: {token[:20]}...")
        
        return True
    
    print("❌ Not authenticated. Starting authentication flow...")
    print()
    
    # Authenticate
    print("🚀 Starting device code flow...")
    print("👀 Watch for the device code prompt below:")
    print("-" * 40)
    
    result = await auth_manager.authenticate()
    
    print("-" * 40)
    
    if result.success:
        print("✅ Authentication successful!")
        if result.user_info:
            print(f"👤 User: {result.user_info.get('name', 'Unknown')}")
        print(f"🔑 Access token: {result.access_token[:20]}...")
        print(f"⏰ Expires in: {result.expires_in} seconds")
        return True
    else:
        print(f"❌ Authentication failed: {result.error}")
        return False


async def test_logout():
    """Test the logout functionality."""
    print("\n🚪 Testing logout...")
    
    try:
        config = AuthConfig.from_env()
        auth_manager = AuthManager(config)
        
        await auth_manager.logout()
        print("✅ Logout successful!")
        
        # Verify we're logged out
        if not auth_manager.is_authenticated():
            print("✅ Authentication cleared successfully!")
        else:
            print("⚠️ Authentication still present after logout")
            
    except Exception as e:
        print(f"❌ Logout failed: {e}")


def main():
    """Main test function."""
    print("Microsoft Entra ID Authentication Test")
    print("=====================================\n")
    
    # Test authentication
    success = asyncio.run(test_authentication())
    
    if success:
        print("\n" + "=" * 50)
        
        # Ask if user wants to test logout
        try:
            response = input("\n🤔 Test logout? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                asyncio.run(test_logout())
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    print("\n🏁 Test complete!")


if __name__ == "__main__":
    main()