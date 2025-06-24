#!/usr/bin/env python3
"""Minimal auth test that skips caching to avoid WSL issues."""

import sys
import os
import msal

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from auth_components import AuthConfig


def simple_device_flow_test():
    """Test device code flow without any caching."""
    print("🔐 Simple Device Code Flow Test (No Caching)")
    print("=" * 50)
    
    try:
        # Load config
        config = AuthConfig.from_env()
        print(f"✅ Client ID: {config.client_id[:8]}...")
        print(f"✅ Tenant ID: {config.tenant_id}")
        print()
        
        # Create MSAL app WITHOUT cache
        print("📱 Creating MSAL app (no cache)...")
        app = msal.PublicClientApplication(
            client_id=config.client_id,
            authority=config.authority,
            # No token_cache parameter = no caching
        )
        print("✅ MSAL app created")
        
        # Start device flow
        print("\n🚀 Starting device code flow...")
        flow = app.initiate_device_flow(scopes=config.scopes)
        
        if "user_code" not in flow:
            print("❌ Failed to initiate device flow")
            print(f"Flow result: {flow}")
            return False
        
        # Show user the device code message
        print("\n" + "="*60)
        print("DEVICE CODE INSTRUCTIONS:")
        print("="*60)
        print(flow["message"])
        print("="*60)
        
        # Wait for user to complete authentication
        print("\n⏳ Waiting for you to complete authentication...")
        print("   (Go to the URL above and enter the code)")
        
        result = app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            print("\n🎉 SUCCESS!")
            print(f"✅ Access token received: {result['access_token'][:20]}...")
            if "id_token_claims" in result:
                claims = result["id_token_claims"]
                print(f"👤 User: {claims.get('name', 'Unknown')}")
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error_description', result.get('error', 'Unknown error'))}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    simple_device_flow_test()