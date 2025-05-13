import os
import uuid
from pathlib import Path
from typing import List, Union
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session


from app.db.models import FileMetadata
from app.modules.content_extraction.services import ContentExtractor
from app.modules.chunking.services import ChunkData
from app.modules.embeddings.services import EmbedderService
from app.core.config import UPLOAD_DIR

# logging configs
from app.core.logging_config import get_logger
logger = get_logger(__name__)


class FileUploadService:
    def __init__(self, db: Session):
        self.db = db
        logger.debug("FileUploadService initialized")

    async def save_uploaded_file(self, file: UploadFile) -> FileMetadata:
        """Save a single uploaded file and return metadata"""
        logger.info(f"Processing file: {file.filename}")
        if not self.db:
            raise HTTPException(
                status_code=500,
                detail="Database session not available"
            )
        
        try:
            # Generate unique filename
            file_ext = Path(file.filename).suffix.lower()
            file_id = str(uuid.uuid4())
            unique_name = f"{file_id}{file_ext}"

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
                file_id=file_id,
                filename=file.filename,
                file_type=file_ext[1:] if file_ext else None,
                file_size=file_size,
                content_type=file.content_type,
                upload_path=str(file_path),
            )
            
            self.db.add(db_file)
            self.db.commit()
            self.db.refresh(db_file)

            logger.debug(f"File {file.filename} saved successfully, size: {file_size} bytes")

            # Now extract content with a fresh database session
            try:
                extractor = ContentExtractor(db=self.db)
                logger.info(f"Starting content extraction: {file.filename}")
                
                # Use the committed file_id
                text_meta = extractor.extract_and_store_content(db_file.id)  # Use the database ID
                
            except Exception as e:
                logger.error(f"Failed to extract content {file.filename}: {str(e)}", exc_info=True)
                # Don't fail the upload if extraction fails
                print(f"Content Extraction error: {e}")

            
            # chunk the extracted data
            try:
                chunker = ChunkData(db=self.db)
                logger.info(f"Starting Text Chunking: {text_meta.text_filename}")

                chunk_meta = chunker.chunk_and_store_text(text_meta.id)

            except Exception as e:
                logger.error(f"Failed to Chunk Text {text_meta.text_filename}: {str(e)}", exc_info=True)

                print(f"Text Chunk error: {e}")

            
            # generate embedding of text chunks and store it in vector DB
            try:
                embedder = EmbedderService(self.db)
                logger.info(f"Starting Text Chunks Embedding: {text_meta.text_filename}")

                embed_meta = embedder.embed_and_store_chunks(text_meta.id)

            except Exception as e:
                 logger.error(f"Failed to Embed Chunk Text {text_meta.text_filename}: {str(e)}", exc_info=True)

            
            return db_file
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save file {file.filename}: {str(e)}", exc_info=True)
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