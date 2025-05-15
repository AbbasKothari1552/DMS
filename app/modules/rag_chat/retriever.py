# --- app/modules/rag_chat/retriever.py ---

from typing import List
from sqlalchemy.orm import Session

from app.modules.vector_store.faiss_handler import FAISSHandler
from app.modules.embeddings.embedder import Embedder
from app.db.models import ChunkMetadata, FileMetadata

# logging configs
from app.core.logging_config import get_logger
logger = get_logger(__name__)


class DocumentRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.embedder = Embedder()
        self.faiss = FAISSHandler()

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Embed the query, perform FAISS search, enrich results with chunk + file metadata.
        """
        
        logger.info(f"Retreiving chunks and metadata...")

        query_vector = self.embedder.embed_texts([query])
        results = self.faiss.search(query_vector, k=top_k)

        response = []
        seen_chunk_ids = set()

        logger.info(f"Result from vectore db:", str(results))

        for meta, score in results:
            chunk_id = meta.get("chunk_id")
            file_id = meta.get("file_id")
            if not chunk_id or chunk_id in seen_chunk_ids:
                continue

            chunk = self.db.query(ChunkMetadata).filter(ChunkMetadata.id == chunk_id).first()
            file = self.db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
            if not chunk or not file:
                continue

            response.append({
                "chunk_text": chunk.chunk_text,
                "file_name": file.filename,
                "file_path": file.upload_path,
                "score": float(score)
            })
            seen_chunk_ids.add(chunk_id)

        logger.debug("Retrieved Response:", str(response))

        return response
