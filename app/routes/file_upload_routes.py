from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List, Union, Dict
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.file_upload.services import FileUploadService
from app.db.models import FileMetadata
# from app.schemas import FileMetadata

from app.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/upload", response_model=Dict)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload files or process directory paths
    
    Parameters:
    - files: List of files to upload
    - paths: List of directory paths to process
    
    Note: For paths, send them as strings in the same multipart form as files
    """
    logger.info(f"Received upload request with {len(files)} files")
    try:
        service = FileUploadService(db)
        results = await service.process_uploaded_items(files)
        success_count = len([r for r in results if isinstance(r, FileMetadata)])
        failed_count = len(results) - success_count

        # Convert FileMetadata objects to dicts for JSON serialization
        serialized_results = []
        for result in results:
            if isinstance(result, FileMetadata):
                serialized_results.append({
                    "filename": result.filename,
                    "file_id": result.file_id,
                    "status": "success",
                    "file_size": result.file_size,
                    "file_type": result.file_type
                })
            else:
                serialized_results.append(result)
        
        logger.info(f"Upload processed successfully: {len(results)} files")
        return {
            "message": "Upload processed",
            "results": serialized_results,
            "success_count": success_count,
            "failed_count": failed_count
        }
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    finally:
        db.close()