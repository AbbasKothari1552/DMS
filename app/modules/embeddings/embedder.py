from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import torch

from app.core.config import EMBEDDING_MODEL

from app.core.logging_config import get_logger
logger = get_logger(__name__)


class Embedder:
    # def __init__(self, model_name: str = EMBEDDING_MODEL):
    #     self.model = SentenceTransformer(model_name)
    #     self.dim = self.model.get_sentence_embedding_dimension()

    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Embedder, cls).__new__(cls)
            # Load the model once when first instantiated
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            cls._model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
            logger.info(f"Loaded model on device: {device}")
        return cls._instance

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of text chunks.
        Returns a numpy array of shape (n_chunks, embedding_dim).
        """
        # embeddings = self.model.encode(texts, show_progress_bar=False)
        # return embeddings
        return self._model.encode(texts)
