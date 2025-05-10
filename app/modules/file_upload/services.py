import os
import uuid
from pathlib import Path
from typing import List, Union
from fastapi import UploadFile, HTTPException, status
from db.session import SessionLocal
from db.models.file_metadata import FileMetadata
from core.config import UPLOAD_DIR

class FileUploadService:
    def __init__(self, db: SessionLocal):
        self.db = db

    async def save_uploaded_file(self, file: UploadFile) -> FileMetadata:
        """Save a single uploaded file and return metadata"""
        if not self.db:
            raise HTTPException(
                status_code=500,
                detail="Database session not available"
            )
        
        try:
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            unique_name = f"{uuid.uuid4()}{file_ext}"

            # Create full path including UPLOAD_DIR
            file_path = Path(UPLOAD_DIR) / unique_name
            # file_path = Path(unique_name)  # Store in root of upload dir
            
            # Ensure upload directory exists
            # full_path = Path(UPLOAD_DIR) / file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  # 1MB chunks
                    buffer.write(chunk)
                    file_size += len(chunk)
            
            # Create metadata record
            db_file = FileMetadata(
                filename=file.filename,
                file_id=unique_name,
                upload_path=str(file_path),
                file_type=file_ext[1:] if file_ext else None,
                file_size=file_size,
                content_type=file.content_type
            )
            
            self.db.add(db_file)
            await self.db.commit()
            await self.db.refresh(db_file)
            
            return db_file
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        finally:
            await file.close()

    async def process_uploaded_items(
        self, 
        items: List[UploadFile]
    ) -> List[Union[FileMetadata, dict]]:
        """Process mixed list of files and folder paths"""
        results = []
        
        for item in items:
            try:
                file_meta = await self.save_uploaded_file(item)
                results.append(file_meta)
            except HTTPException as e:
                results.append({
                    "filename": item.filename,
                    "error": e.detail,
                    "status": "failed"
                })
            except Exception as e:
                results.append({
                    "path": str(item),
                    "error": str(e),
                    "status": "failed"
                })
                
        return results