"""OneDrive client for file operations."""

import asyncio
import aiohttp
from typing import List, Optional, Union, Dict, Any
from pathlib import Path

from .models import OneDriveFile, OneDriveFolder, FileUploadResult, FileDownloadResult


class OneDriveClient:
    """Simple OneDrive client using Microsoft Graph API."""
    
    def __init__(self, access_token: str):
        """Initialize OneDrive client with access token."""
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def list_root_items(self) -> List[Union[OneDriveFile, OneDriveFolder]]:
        """List items in the root folder."""
        return await self.list_folder_items()
    
    async def list_folder_items(self, folder_id: Optional[str] = None) -> List[Union[OneDriveFile, OneDriveFolder]]:
        """List items in a specific folder or root if folder_id is None."""
        if folder_id:
            url = f"{self.base_url}/me/drive/items/{folder_id}/children"
        else:
            url = f"{self.base_url}/me/drive/root/children"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    items = []
                    
                    for item in data.get("value", []):
                        if "folder" in item:
                            items.append(OneDriveFolder.from_graph_data(item))
                        else:
                            items.append(OneDriveFile.from_graph_data(item))
                    
                    return items
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to list items: {response.status} - {error_text}")
    
    async def get_file_info(self, file_id: str) -> OneDriveFile:
        """Get detailed information about a specific file."""
        url = f"{self.base_url}/me/drive/items/{file_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return OneDriveFile.from_graph_data(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to get file info: {response.status} - {error_text}")
    
    async def download_file(self, file_id: str) -> FileDownloadResult:
        """Download a file by ID."""
        try:
            # First get file info to get download URL
            file_info = await self.get_file_info(file_id)
            
            if not file_info.download_url:
                return FileDownloadResult(
                    success=False,
                    error="No download URL available for this file"
                )
            
            # Download the file content
            async with aiohttp.ClientSession() as session:
                async with session.get(file_info.download_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        return FileDownloadResult(
                            success=True,
                            content=content,
                            file_name=file_info.name,
                            mime_type=file_info.mime_type
                        )
                    else:
                        error_text = await response.text()
                        return FileDownloadResult(
                            success=False,
                            error=f"Download failed: {response.status} - {error_text}"
                        )
        
        except Exception as e:
            return FileDownloadResult(
                success=False,
                error=f"Download error: {str(e)}"
            )
    
    async def upload_file(self, file_path: Union[str, Path], 
                         folder_id: Optional[str] = None,
                         filename: Optional[str] = None) -> FileUploadResult:
        """Upload a file to OneDrive."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return FileUploadResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Use provided filename or original filename
            upload_name = filename or file_path.name
            
            # Determine upload URL
            if folder_id:
                url = f"{self.base_url}/me/drive/items/{folder_id}:/{upload_name}:/content"
            else:
                url = f"{self.base_url}/me/drive/root:/{upload_name}:/content"
            
            # Upload file
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream"
            }
            
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as f:
                    async with session.put(url, headers=headers, data=f) as response:
                        if response.status in [200, 201]:
                            data = await response.json()
                            return FileUploadResult(
                                success=True,
                                file_id=data["id"],
                                file_name=data["name"],
                                size=data["size"]
                            )
                        else:
                            error_text = await response.text()
                            return FileUploadResult(
                                success=False,
                                error=f"Upload failed: {response.status} - {error_text}"
                            )
        
        except Exception as e:
            return FileUploadResult(
                success=False,
                error=f"Upload error: {str(e)}"
            )
    
    async def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[OneDriveFolder]:
        """Create a new folder."""
        try:
            if parent_folder_id:
                url = f"{self.base_url}/me/drive/items/{parent_folder_id}/children"
            else:
                url = f"{self.base_url}/me/drive/root/children"
            
            data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    if response.status == 201:
                        result = await response.json()
                        return OneDriveFolder.from_graph_data(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to create folder: {response.status} - {error_text}")
        
        except Exception as e:
            raise Exception(f"Create folder error: {str(e)}")
    
    async def delete_item(self, item_id: str) -> bool:
        """Delete a file or folder."""
        try:
            url = f"{self.base_url}/me/drive/items/{item_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    return response.status == 204
        
        except Exception:
            return False
    
    async def search_files(self, query: str) -> List[OneDriveFile]:
        """Search for files by name."""
        try:
            url = f"{self.base_url}/me/drive/root/search(q='{query}')"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        files = []
                        
                        for item in data.get("value", []):
                            if "file" in item:  # Only return files, not folders
                                files.append(OneDriveFile.from_graph_data(item))
                        
                        return files
                    else:
                        error_text = await response.text()
                        raise Exception(f"Search failed: {response.status} - {error_text}")
        
        except Exception as e:
            raise Exception(f"Search error: {str(e)}")