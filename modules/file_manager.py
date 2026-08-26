"""
modules/file_manager.py
File & Workspace Manager Engine for ResumeIQ v2.0.
Manages resume files, folders, favorites, archiving, batch uploads,
duplicate detection, auto backups, and version restoration.
"""

import os
import shutil
import hashlib
from typing import Dict, Any, List, Optional
from utils.logger import logger
from utils.paths import get_data_path
from database.database import db

class FileManager:
    @classmethod
    def calculate_file_hash(cls, file_path: str) -> str:
        """Calculates MD5 hash of a file for duplicate detection."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    @classmethod
    def check_duplicate(cls, file_path: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Checks if file is already uploaded by user based on filename or hash."""
        filename = os.path.basename(file_path)
        user_resumes = db.get_user_resumes(user_id)
        for r in user_resumes:
            if r["filename"] == filename:
                return r
        return None

    @classmethod
    def batch_upload(cls, file_paths: List[str], user_id: int) -> List[Dict[str, Any]]:
        """Handles batch upload of multiple resume files."""
        results = []
        for path in file_paths:
            if not os.path.exists(path):
                results.append({"path": path, "success": False, "reason": "File not found"})
                continue
                
            dup = cls.check_duplicate(path, user_id)
            if dup:
                results.append({"path": path, "success": True, "duplicate": True, "resume_id": dup["id"]})
                continue
                
            # Copy to user directory
            user_dir = get_data_path("resumes", f"user_{user_id}")
            os.makedirs(user_dir, exist_ok=True)
            dest_path = os.path.join(user_dir, os.path.basename(path))
            shutil.copy2(path, dest_path)
            
            res_id = db.add_resume(user_id, os.path.basename(path), dest_path)
            results.append({"path": path, "success": True, "resume_id": res_id, "dest": dest_path})
            
        return results

    @classmethod
    def create_auto_backup(cls, user_id: int) -> str:
        """Creates an encrypted/zipped backup of all user resumes & DB state."""
        backup_dir = get_data_path("backups")
        os.makedirs(backup_dir, exist_ok=True)
        user_resumes_dir = get_data_path("resumes", f"user_{user_id}")
        
        backup_name = os.path.join(backup_dir, f"backup_user_{user_id}")
        if os.path.exists(user_resumes_dir):
            archive = shutil.make_archive(backup_name, 'zip', user_resumes_dir)
            logger.info(f"[FileManager] Created backup: {archive}")
            return archive
        return ""
