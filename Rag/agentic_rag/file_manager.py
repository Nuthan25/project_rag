import os
import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime

class FileManager:
    """Manages file metadata and unique identifiers"""
    def __init__(self, metadata_path: str = "file_metadata.json"):
        self.metadata_path = metadata_path
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load existing metadata or create new"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def register_file(self, file_path: str, file_type: str) -> str:
        """Register a new file and return unique ID"""
        file_id = str(uuid.uuid4())[:8]
        self.metadata[file_id] = {
            "file_path": file_path,
            "file_type": file_type,
            "filename": os.path.basename(file_path),
            "created_at": datetime.now().isoformat(),
            "status": "registered"
        }
        self._save_metadata()
        return file_id

    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information by ID"""
        return self.metadata.get(file_id)

    def update_file_status(self, file_id: str, status: str):
        """Update file processing status"""
        if file_id in self.metadata:
            self.metadata[file_id]["status"] = status
            self._save_metadata()

    def get_all_files(self) -> Dict[str, Any]:
        """Get all registered files"""
        return self.metadata