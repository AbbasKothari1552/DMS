from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List, Union, Dict
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.db.session import get_db
from app.modules.file_upload.services import FileUploadService
from app.modules.content_extraction.services import ContentExtractor
from app.modules.chunking.services import ChunkData
from app.modules.embeddings.services import EmbedderService
from app.db.models import FileMetadata, TextMetaData
from app.core.config import UPLOAD_DIR


from app.core.logging_config import get_logger
logger = get_logger(__name__)

router = APIRouter()


async def cleanup_on_failure(file_path: str = None, db: Session = None, file_meta_id: int = None):
    """Cleanup resources when processing fails"""
    try:
        # Remove uploaded file if exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
            
        # Remove database entries if exists
        if db and file_meta_id:
            # Delete any related records in reverse dependency order
            db.query(TextMetaData).filter(TextMetaData.file_id == file_meta_id).delete()
            db.query(FileMetadata).filter(FileMetadata.id == file_meta_id).delete()
            db.commit()
            logger.info(f"Cleaned up database records for file_id: {file_meta_id}")
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        db.rollback()


@router.post("/upload", response_model=Dict)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload files and process them through the pipeline:
    1. File upload and metadata creation
    2. Content extraction
    3. Text chunking
    4. Embedding generation
    """
    logger.info(f"Received upload request with {len(files)} files")
    results = []
    for file in files:
        file_path = None
        file_meta = None
        try:
            # Initialize services
            upload_service = FileUploadService(db)
            
            # Step 1: Save uploaded file - we commit this immediately since the file is already saved
            file_meta = await upload_service.save_uploaded_file(file)
            file_path = Path(UPLOAD_DIR) / f"{file_meta.file_id}{Path(file.filename).suffix.lower()}"
            

            try:
                logger.debug("Starting other modules...")
                
                # Initialize processing services
                extractor = ContentExtractor(db)
                chunker = ChunkData(db)
                embedder = EmbedderService(db)
                
                # Step 2: Extract content
                text_meta = extractor.extract_and_store_content(file_meta.id)
                
                # Step 3: Chunk text
                chunk_meta = chunker.chunk_and_store_text(text_meta.id)
                
                # Step 4: Generate embeddings
                embed_meta = embedder.embed_and_store_chunks(text_meta.id)
                
                # Commit the processing pipeline
                db.commit()

                logger.info(f"Processed: {file_meta.filename}")
                
                results.append({
                    "filename": file_meta.filename,
                    "file_id": file_meta.file_id,
                    "status": "success",
                    "file_size": file_meta.file_size,
                    "file_type": file_meta.file_type
                })
                
            except Exception as processing_error:
                db.rollback()
                await cleanup_on_failure(str(file_path), db, file_meta.id)
                results.append({
                    "filename": file.filename, 
                    "status": "failed", 
                    "error": str(processing_error)
                })
                raise HTTPException(
                    status_code=500,
                    detail=f"File processing failed: {str(processing_error)}"
                )
                
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": e.detail
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
        finally:
            await file.close()
    
    success_count = len([r for r in results if r.get("status") == "success"])
    failed_count = len(results) - success_count

    from pprint import pprint
    pprint({
        "message": "Upload processed",
        "results": results,
        "successful": [r for r in results if r["status"] == "success"],
        "failed": [r for r in results if r["status"] == "failed"],
    })
    
    return {
        "message": "Upload processed",
        "results": results,
        "successful": [r for r in results if r["status"] == "success"],
        "failed": [r for r in results if r["status"] == "failed"],
    }