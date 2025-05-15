from typing import List

from app.modules.rag_chat.llm_engine import LLMEngine

# logging configs
from app.core.logging_config import get_logger
logger = get_logger(__name__)

class RAGChain:
    def __init__(self):
        self.llm_engine = LLMEngine()

    def build_prompt(self, query: str, contexts: List[str]) -> str:
        """
        Combine context chunks and user query into a single prompt.
        """

        logger.info(f"Building Prompt for chain")

        context_block = "\n\n".join(contexts)
        prompt = f"""
            You are an AI assistant. Use the following document excerpts to answer the question as accurately as possible.
            If the answer is not contained in the documents, say you don't know.

            Context:
            {context_block}

            Question: {query}
            Answer:
        """
        return prompt.strip()

    def run(self, query: str, chunks: List[dict]) -> str:
        """
        Build RAG prompt and generate answer.
        """
        contexts = [chunk["chunk_text"] for chunk in chunks]
        prompt = self.build_prompt(query, contexts)
        return self.llm_engine.generate(prompt)
