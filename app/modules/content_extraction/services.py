from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import BASE_PATH, CONTENT_EXTRACTION_DIR
from app.db.models import TextMetaData, FileMetadata

# Import extractors
from app.modules.content_extraction.extractors.docs import extract_docx_text
from app.modules.content_extraction.extractors.pdf import extract_pdf_text
from app.modules.content_extraction.extractors.image import extract_image_text
from app.modules.content_extraction.extractors.excel import extract_excel_text

from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ContentExtractor:
    def __init__(self, db: Session):
        self.db = db
        self.content_dir = Path(CONTENT_EXTRACTION_DIR)
        self.content_dir.mkdir(parents=True, exist_ok=True)

    def get_extractor(self, file_type: str):
        """Get appropriate extractor based on file type"""
        file_type = file_type.lower()
        if file_type == "pdf":
            return extract_pdf_text
        elif file_type in ["doc", "docx"]:
            return extract_docx_text
        elif file_type in ["xls", "xlsx"]:
            return extract_excel_text
        elif file_type in ["jpg", "jpeg", "png", "tiff"]:
            return extract_image_text
        return None

    def extract_and_store_content(self, file_id: int) -> TextMetaData:
        """Main extraction method"""
        logger.info(f"Starting text extraction for file_id: {file_id}")
        
        # Step 1: Retrieve FileMetadata
        file_meta = self.db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
        if not file_meta:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Step 2: Check if already processed
        existing_text_meta = self.db.query(TextMetaData).filter(TextMetaData.file_id == file_id).first()
        if existing_text_meta and existing_text_meta.extraction_status == "completed":
            logger.info(f"Text already extracted for file_id: {file_id}")
            return existing_text_meta
            
        extractor = self.get_extractor(file_meta.file_type)
        if not extractor:
            logger.warning(f"No extractor available for file type: {file_meta.file_type}")
            file_meta.extraction_status = "failed"
            self.db.commit()
            return file_meta
        
        try:
            # Step 4: Define output path
            content_filename = f"{file_meta.file_id}.txt"
            content_path = self.content_dir / content_filename

            input_path = BASE_PATH / Path(file_meta.upload_path)
            
            logger.info(f"Extracting content from: {file_meta.upload_path}")
            logger.info(f"Saving extracted content to: {content_path}")
            
            # Step 5: Perform extraction
            result = extractor(
                input_path=input_path,
                output_path=str(content_path)
            )
            
            # Step 6: Create or update TextMetaData
            if not existing_text_meta:
                text_meta = TextMetaData(
                    file_id=file_id,
                    text_filename = content_filename,
                    upload_path = str(content_path),
                    extraction_status="completed"
                )
                self.db.add(text_meta)
            else:
                text_meta = existing_text_meta
                text_meta.upload_path = content_filename
                text_meta.extraction_status = "completed"
                
            self.db.commit()
            self.db.refresh(text_meta)

            logger.info(f"Extraction and storage completed for file_id: {file_id}")
            return text_meta
            
        except Exception as e:
            logger.error(f"Extraction failed for {file_meta.filename}: {str(e)}")
            
            self.db.rollback()

            # Update status to failed if metadata exists
            if existing_text_meta:
                existing_text_meta.extraction_status = "failed"
                self.db.commit()

            raise HTTPException(
                status_code=500,
                detail=f"Content extraction failed: {str(e)}"
            )