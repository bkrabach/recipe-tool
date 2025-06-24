#!/usr/bin/env python3
"""Quick test to verify auth components work without actual authentication."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all imports work."""
    print("🔍 Testing imports...")
    try:
        from auth_components import AuthManager, AuthResult, AuthConfig
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation."""
    print("\n🔍 Testing configuration validation...")
    try:
        from auth_components import AuthConfig
        
        # Save existing env vars
        old_client_id = os.environ.get('ENTRA_CLIENT_ID')
        old_tenant_id = os.environ.get('ENTRA_TENANT_ID')
        
        # Clear env vars
        if 'ENTRA_CLIENT_ID' in os.environ:
            del os.environ['ENTRA_CLIENT_ID']
        if 'ENTRA_TENANT_ID' in os.environ:
            del os.environ['ENTRA_TENANT_ID']
        
        # Test missing environment variables
        try:
            config = AuthConfig.from_env()
            print(f"❌ Should have failed with missing env vars, but got config with client_id='{config.client_id}', tenant_id='{config.tenant_id}'")
            return False
        except ValueError as e:
            print(f"✅ Correctly caught missing env vars: {e}")
        
        # Test with dummy variables
        os.environ['ENTRA_CLIENT_ID'] = 'test-client-id'
        os.environ['ENTRA_TENANT_ID'] = 'test-tenant-id'
        
        config = AuthConfig.from_env()
        print("✅ Config created with env vars")
        print(f"  Client ID: {config.client_id}")
        print(f"  Tenant ID: {config.tenant_id}")
        print(f"  Authority: {config.authority}")
        print(f"  Scopes: {config.scopes}")
        
        # Restore original env vars
        if old_client_id:
            os.environ['ENTRA_CLIENT_ID'] = old_client_id
        elif 'ENTRA_CLIENT_ID' in os.environ:
            del os.environ['ENTRA_CLIENT_ID']
            
        if old_tenant_id:
            os.environ['ENTRA_TENANT_ID'] = old_tenant_id
        elif 'ENTRA_TENANT_ID' in os.environ:
            del os.environ['ENTRA_TENANT_ID']
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_auth_manager_creation():
    """Test AuthManager creation."""
    print("\n🔍 Testing AuthManager creation...")
    try:
        from auth_components import AuthManager, AuthConfig
        
        config = AuthConfig(
            client_id="test-id",
            tenant_id="test-tenant", 
            scopes=["test-scope"],
            authority="https://test.authority",
            cache_path="test-cache"
        )
        
        auth_manager = AuthManager(config)
        print("✅ AuthManager created successfully")
        return True
        
    except Exception as e:
        print(f"❌ AuthManager creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Quick Auth Components Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config_validation,
        test_auth_manager_creation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Auth components are working correctly.")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)