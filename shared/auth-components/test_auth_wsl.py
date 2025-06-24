#!/usr/bin/env python3
"""WSL-friendly test script for Microsoft Entra ID authentication."""

import asyncio
import sys
import os
import signal
from datetime import datetime

# Add the current directory to Python path so we can import auth_components
sys.path.insert(0, os.path.dirname(__file__))

from auth_components import AuthManager, AuthConfig


def timeout_handler(signum, frame):
    print("\n❌ Operation timed out! This might be a WSL networking issue.")
    print("Try these troubleshooting steps:")
    print("1. Check your internet connection")
    print("2. Try running: sudo apt update && sudo apt install ca-certificates")
    print("3. Test DNS: nslookup login.microsoftonline.com")
    sys.exit(1)


async def test_auth_with_timeout():
    """Test authentication with better error handling and timeouts."""
    print("🔐 Testing Microsoft Entra ID Authentication (WSL-friendly)")
    print("=" * 60)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = AuthConfig.from_env()
        print(f"✅ Client ID: {config.client_id[:8]}...")
        print(f"✅ Tenant ID: {config.tenant_id}")
        print(f"✅ Authority: {config.authority}")
        print(f"✅ Scopes: {', '.join(config.scopes)}")
        print()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Create auth manager
    auth_manager = AuthManager(config)
    
    # Check for cached tokens with timeout
    print("🔍 Checking for cached authentication...")
    print("  (This might take a moment in WSL...)")
    
    try:
        # Set a timeout for the authentication check
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # 30 second timeout
        
        is_auth = auth_manager.is_authenticated()
        signal.alarm(0)  # Clear timeout
        
        if is_auth:
            print("✅ Already authenticated!")
            
            # Get user info
            user_info = auth_manager.get_user_info()
            if user_info:
                print(f"👤 User: {user_info.get('username', 'Unknown')}")
            
            # Test getting access token
            print("🔑 Getting access token...")
            signal.alarm(30)
            token = await auth_manager.get_access_token()
            signal.alarm(0)
            
            if token:
                print(f"✅ Access token: {token[:20]}...")
                return True
            else:
                print("❌ Failed to get access token")
                return False
        
        print("❌ Not authenticated. Starting device code flow...")
        
    except Exception as e:
        signal.alarm(0)
        print(f"❌ Error checking authentication: {e}")
        print("This might be a network or WSL issue.")
        return False
    
    # Start device code authentication
    print("\n🚀 Starting device code authentication...")
    print("⚠️  Make sure you can access the internet from WSL")
    print("-" * 50)
    
    try:
        signal.alarm(120)  # 2 minute timeout for device flow
        result = await auth_manager.authenticate()
        signal.alarm(0)
        
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
            
    except Exception as e:
        signal.alarm(0)
        print(f"❌ Authentication error: {e}")
        return False


def test_network_connectivity():
    """Test basic network connectivity to Microsoft endpoints."""
    print("🌐 Testing network connectivity...")
    
    import subprocess
    
    endpoints = [
        "login.microsoftonline.com",
        "graph.microsoft.com"
    ]
    
    for endpoint in endpoints:
        try:
            result = subprocess.run(
                ["nslookup", endpoint], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ {endpoint} - DNS resolution OK")
            else:
                print(f"❌ {endpoint} - DNS resolution failed")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print()


def main():
    """Main test function with better error handling."""
    print(f"🕐 Started at: {datetime.now()}")
    print()
    
    # Test network first
    test_network_connectivity()
    
    # Test authentication
    try:
        success = asyncio.run(test_auth_with_timeout())
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 Authentication test completed successfully!")
        else:
            print("\n" + "=" * 60)
            print("❌ Authentication test failed.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🕐 Finished at: {datetime.now()}")


if __name__ == "__main__":
    main()