from sqlalchemy.orm import Session
from fastapi import HTTPException


from langchain.text_splitter import RecursiveCharacterTextSplitter


from app.db.models import TextMetaData, ChunkMetadata


from app.core.logging_config import get_logger
logger = get_logger(__name__)



class ChunkData:

    def __init__(self, db: Session):
        self.db = db

    
    def save_chunk(self, text_file_id: int, chunk_index: int, chunk_text: str) -> ChunkMetadata:
        """
        Saving each chunk with its text file id
        """
        if not self.db:
            raise HTTPException(
                status_code=500,
                detail="Database session not available"
            )
        
        logger.debug(f"Chunk {chunk_index} preview: {chunk_text[:50]}...")

        try:
            db_chunk = ChunkMetadata(
                text_metadata_id=text_file_id,
                chunk_index=chunk_index,
                chunk_text=chunk_text
            )

            self.db.add(db_chunk)
            self.db.commit()
            self.db.refresh(db_chunk)

            logger.debug(f"Chunk: {chunk_index} saved successfully.")
            return db_chunk

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save chunk {chunk_index}: {str(e)}")
            raise


    def chunk_and_store_text(self, text_file_id: int) -> list[ChunkMetadata]:
        """
        Main Chunking Text Method
        """
        logger.info(f"Starting  Chunking of text for file_id: {text_file_id}")

        # Step 1: Retrieve TextMetaData
        text_file_meta = self.db.query(TextMetaData).filter(TextMetaData.id == text_file_id).first()
        if not text_file_meta:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Step 3: Extract all text from file
        content_file_path = text_file_meta.upload_path
        with open(content_file_path, encoding="utf-8") as f:
            text = f.read()

        # Step 4: Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.create_documents([text])


        try:
            logger.debug(f"Total chunks for file {text_file_id}: {len(chunks)}")

            # Step 5: Save each chunk into database
            chunk_db = []
            for index, chunk in enumerate(chunks):
                chunk_db.append(self.save_chunk(text_file_id, index, chunk.page_content))

            logger.debug(f"All Chunks saves successfully")
        
        except Exception as e:
            logger.error(f"Extraction failed for {text_file_meta.text_filename}: {str(e)}")

            self.db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Chunking text failed: {str(e)}"
            )
        
        return chunk_db

