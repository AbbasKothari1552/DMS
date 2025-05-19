from fastapi import HTTPException
from sqlalchemy.orm import Session


from app.modules.embeddings.embedder import Embedder
from app.modules.vector_store.faiss_handler import FAISSHandler
from app.db.models import ChunkMetadata, TextMetaData
from app.core.config import EMBEDDING_DIM

from app.core.logging_config import get_logger
logger = get_logger(__name__)

class EmbedderService:

    def __init__(self, db: Session, dim: int = EMBEDDING_DIM):
        self.db = db
        self.embedder = Embedder()
        self.faiss_handler = FAISSHandler()

    def embed_and_store_chunks(self, text_file_id: int):

        if not self.db:
            raise HTTPException(
                status_code=500,
                detail="Database session not available"
            )
        
        logger.info(f"Starting  embedding of chunked text for file_id: {text_file_id}")

        # step 1: create instance of vector db
        # embedder = Embedder()
        # faiss_handler = FAISSHandler()  # MiniLM model has 384 dim

        # Step 2: Get all chunks for given id
        text_meta = self.db.query(ChunkMetadata).filter(ChunkMetadata.text_metadata_id == text_file_id).all()
        if not text_meta:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            # Step 3: Extract chunk text and metadata
            chunk_texts = [chunk.chunk_text for chunk in text_meta]
            metadata = [{
                "chunk_id": chunk.id, 
                "text_metadata_id": chunk.text_metadata_id,
                "file_id": chunk.file_id
                } for chunk in text_meta]

            # Step 4: Generate embeddings
            vectors = self.embedder.embed_texts(chunk_texts)

            # Step 5: Add to FAISS and get vector IDs
            vector_ids = self.faiss_handler.add_embeddings(vectors, metadata)

            # Step 6: Update DB with vector IDs
            for chunk, vector_id in zip(text_meta, vector_ids):
                chunk.vector_id = vector_id

            self.db.commit()

            logger.info(f"Embedded Successfully for text_file: {text_file_id}")

            return {
                "file_id": text_file_id,
                "chunks_processed": len(text_meta),
                "vector_ids": vector_ids
            }

        except Exception as e:

            logger.error(f"Extraction failed for {text_meta[0].text_filename}: {str(e)}")

            self.db.rollback()

            raise HTTPException(
                status_code=500,
                detail=f"Embedding failed: {str(e)}"
            )
