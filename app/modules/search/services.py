from fastapi import HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.modules.vector_store.faiss_handler import FAISSHandler
from app.modules.embeddings.embedder import Embedder
from app.db.models import ChunkMetadata, FileMetadata


from app.core.logging_config import get_logger
logger = get_logger(__name__)


class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedder = Embedder()
        self.faiss = FAISSHandler()

    def semantic_search(self, query: str, top_k: int = 5) -> List[dict]:

        logger.info(f"Starting semantic search for query: {query}")

        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        try:

            query_vector = self.embedder.embed_texts([query])  # shape: (1, dim)
            results = self.faiss.search(query_vector, k=top_k)

            logger.debug(f"Vectore DB result[0]: {results[0]}")

            response = []
            for meta, score in results:
                chunk = self.db.query(ChunkMetadata).filter(ChunkMetadata.id == meta["chunk_id"]).first()
                if not chunk:
                    continue

                file = self.db.query(FileMetadata).filter(FileMetadata.id == meta["file_id"]).first()
                if not file:
                    continue

                response.append({
                    "chunk_text": chunk.chunk_text[:300],
                    "file_name": file.filename,
                    "file_path": file.upload_path,
                    "score": score
                })

            logger.debug(f"Response[0]: {response[0]}")
            
            logger.info(f"Returned response successfully.")

            return response
        
        except Exception as e:

            logger.error(f"Semantic Search Failed: {str(e)}")

            raise HTTPException(
                status_code=500,
                detail=f"Semantic Search Failed: {str(e)}"
            )


# if __name__ == '__main__':

#     from fastapi import Depends
#     from app.db.session import get_db

#     from pprint import pprint

#     query = "Module 6: semantic search internface"

#     db_gen = get_db()
#     db = next(db_gen)

#     try:
#         service = SemanticSearchService(db)
#         results = service.semantic_search(query)

#         for res in results:
#             pprint(res)

#     finally:
#         db.close()  