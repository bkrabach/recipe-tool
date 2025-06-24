"""Data models for OneDrive operations."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class OneDriveFile:
    """Represents a file in OneDrive."""
    id: str
    name: str
    size: int
    created_datetime: datetime
    modified_datetime: datetime
    download_url: Optional[str] = None
    parent_id: Optional[str] = None
    web_url: Optional[str] = None
    mime_type: Optional[str] = None
    
    @classmethod
    def from_graph_data(cls, data: Dict[str, Any]) -> "OneDriveFile":
        """Create OneDriveFile from Microsoft Graph API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            size=data.get("size", 0),
            created_datetime=datetime.fromisoformat(data["createdDateTime"].replace("Z", "+00:00")),
            modified_datetime=datetime.fromisoformat(data["lastModifiedDateTime"].replace("Z", "+00:00")),
            download_url=data.get("@microsoft.graph.downloadUrl"),
            parent_id=data.get("parentReference", {}).get("id"),
            web_url=data.get("webUrl"),
            mime_type=data.get("file", {}).get("mimeType")
        )


@dataclass
class OneDriveFolder:
    """Represents a folder in OneDrive."""
    id: str
    name: str
    created_datetime: datetime
    modified_datetime: datetime
    child_count: int = 0
    parent_id: Optional[str] = None
    web_url: Optional[str] = None
    
    @classmethod
    def from_graph_data(cls, data: Dict[str, Any]) -> "OneDriveFolder":
        """Create OneDriveFolder from Microsoft Graph API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_datetime=datetime.fromisoformat(data["createdDateTime"].replace("Z", "+00:00")),
            modified_datetime=datetime.fromisoformat(data["lastModifiedDateTime"].replace("Z", "+00:00")),
            child_count=data.get("folder", {}).get("childCount", 0),
            parent_id=data.get("parentReference", {}).get("id"),
            web_url=data.get("webUrl")
        )


@dataclass
class FileUploadResult:
    """Result of a file upload operation."""
    success: bool
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[int] = None
    error: Optional[str] = None
    

@dataclass
class FileDownloadResult:
    """Result of a file download operation."""
    success: bool
    content: Optional[bytes] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    error: Optional[str] = None