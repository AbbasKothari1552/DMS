# --- app/modules/rag_chat/services.py ---

from sqlalchemy.orm import Session
from app.modules.rag_chat.retriever import DocumentRetriever
from app.modules.rag_chat.rag_chain import RAGChain

# logging configs
from app.core.logging_config import get_logger
logger = get_logger(__name__)

class RAGQAService:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = DocumentRetriever(db)
        self.rag_chain = RAGChain()

    def answer_query(self, query: str, top_k: int = 5) -> dict:
        """
        End-to-end method: retrieves, constructs prompt, gets LLM response.
        """

        logger.info(f"Starting rag query process")

        relevant_chunks = self.retriever.retrieve_relevant_chunks(query, top_k=top_k)
        if not relevant_chunks:
            return {
                "answer": "Sorry, I couldn't find any relevant information.",
                "references": []
            }

        logger.info(f"Running rag chain")
        answer = self.rag_chain.run(query, relevant_chunks)

        logger.info(f"Answer generated using llm:", answer)

        return {
            "answer": answer,
            "references": [
                {
                    "file_name": item["file_name"],
                    "file_path": item["file_path"],
                    "score": item["score"],
                    "snippet": item["chunk_text"][:300]  # trimmed for preview
                }
                for item in relevant_chunks
            ]
        }
