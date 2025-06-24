# Auth Components

Microsoft Entra ID authentication components for Recipe Tool projects using device code flow.

## Features

- Device code flow authentication (perfect for desktop/CLI apps)
- Automatic token caching and refresh
- Simple, minimal API following project philosophy
- Environment variable configuration

## Quick Start

1. **Configure your Entra ID app** to allow device code flow
2. **Set up environment variables** (copy `.env.example` to `.env`)
3. **Test authentication**:

```bash
cd shared/auth-components
python test_auth.py
```

## Usage

```python
import asyncio
from auth_components import AuthManager, AuthConfig

async def main():
    # Load config from environment
    config = AuthConfig.from_env()
    
    # Create auth manager
    auth = AuthManager(config)
    
    # Authenticate (will prompt for device code if needed)
    result = await auth.authenticate()
    
    if result.success:
        print(f"Authenticated! Token: {result.access_token[:20]}...")
        
        # Get access token for API calls
        token = await auth.get_access_token()
        
        # Check auth status
        if auth.is_authenticated():
            print("Still authenticated!")
    else:
        print(f"Auth failed: {result.error}")

asyncio.run(main())
```

## Configuration

Set these environment variables (or use a `.env` file):

```bash
ENTRA_CLIENT_ID=your-client-id
ENTRA_TENANT_ID=your-tenant-id
```

Optional variables:
```bash
ENTRA_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
ENTRA_SCOPES=https://graph.microsoft.com/.default
TOKEN_CACHE_PATH=.auth_cache
```

## Entra ID App Setup

Your Entra ID application needs:

1. **Platform configuration**: Mobile and desktop applications
2. **Redirect URI**: `http://localhost` (for device code flow)
3. **API permissions**:
   - `Microsoft Graph` > `Files.ReadWrite.All` (for OneDrive)
   - `Microsoft Graph` > `User.Read` (for user info)
4. **Grant admin consent** for the permissions

## Architecture

- `AuthConfig`: Environment-based configuration
- `AuthManager`: Main authentication interface  
- `AuthResult`: Authentication result data
- Token caching handled automatically via MSAL

Follows "ruthless simplicity" - minimal wrapper around MSAL with just essential functionality.