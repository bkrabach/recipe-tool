# Shared Components

This directory contains reusable components for the Recipe Tool project, following a modular "bricks and studs" architecture.

## 🧱 Components

### auth-components
Microsoft Entra ID authentication using MSAL device code flow.

**Features:**
- Environment-based configuration
- Token caching and automatic refresh
- Device code authentication flow
- User profile information

**Usage:**
```python
from auth_components import AuthManager, AuthConfig

config = AuthConfig.from_env()
auth_manager = AuthManager(config)

# Authenticate user
result = await auth_manager.authenticate()
if result.success:
    token = await auth_manager.get_access_token()
```

### onedrive-components
Microsoft OneDrive integration using Graph API.

**Features:**
- File listing and navigation
- Upload and download operations
- Search functionality
- Folder management

**Usage:**
```python
from onedrive_components import OneDriveClient

client = OneDriveClient(access_token)
files = await client.list_root_items()
upload_result = await client.upload_file("local_file.txt")
```

### gradio-auth-components
Gradio UI components for authentication flows.

**Features:**
- Complete authentication interface
- Simple authentication button
- Status displays and user information
- Device code flow UI

**Usage:**
```python
from gradio_auth_components import AuthenticationUI

auth_ui = AuthenticationUI(auth_config)
interface = auth_ui.create_auth_interface()
```

## 📋 Configuration

Create a `.env` file in `auth-components/`:

```env
# Microsoft Entra ID Configuration
ENTRA_CLIENT_ID=your-client-id-here
ENTRA_TENANT_ID=your-tenant-id-here

# Optional: Custom scopes (defaults to User.Read,Files.ReadWrite.All)
# ENTRA_SCOPES=User.Read,Files.ReadWrite.All

# Optional: Custom authority URL
# ENTRA_AUTHORITY=https://login.microsoftonline.com/your-tenant-id

# Optional: Token cache path (defaults to .auth_cache)
# TOKEN_CACHE_PATH=.auth_cache
```

## 🎯 Personal OneDrive Setup

For personal Microsoft accounts:

1. **Create app registration** with `signInAudience: "PersonalMicrosoftAccount"`
2. **Add permissions**: `User.Read`, `Files.ReadWrite.All`
3. **Use tenant ID**: `common` or `consumers` 
4. **Set authority**: `https://login.microsoftonline.com/common`

## 🔗 Integration

Components are designed to work together:

```python
# Complete integration example
from auth_components import AuthManager, AuthConfig
from onedrive_components import OneDriveClient
from gradio_auth_components import AuthenticationUI

# Setup
config = AuthConfig.from_env()
auth_manager = AuthManager(config)
auth_ui = AuthenticationUI(config)

# Authenticate
result = await auth_manager.authenticate()
if result.success:
    # Use OneDrive
    onedrive = OneDriveClient(result.access_token)
    files = await onedrive.list_root_items()
```

## 📦 Dependencies

All components are workspace packages and automatically installed with:

```bash
make install
```