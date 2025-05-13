from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

from app.core.config import EMBEDDING_MODEL


class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks.
        Returns a numpy array of shape (n_chunks, embedding_dim).
        """
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings
