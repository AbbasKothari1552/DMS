import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

from app.core.config import FAISS_INDEX_PATH, FAISS_METADATA_PATH, EMBEDDING_MODEL

from app.core.logging_config import get_logger
logger = get_logger(__name__)


class FAISSHandler:
    def __init__(self, model_name: str = EMBEDDING_MODEL, index_path: str = FAISS_INDEX_PATH, metadata_path: str = FAISS_METADATA_PATH):
        
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index_path = index_path
        self.metadata_path = metadata_path

        # Load or create index
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            self.metadata = self._load_metadata()
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            self.metadata = []

    def add_embeddings(self, embeddings: np.ndarray, metadata: list):
        """
        Adds embeddings and stores metadata (like chunk_id, file_id).
        """
        self.index.add(embeddings)
        self.metadata.extend(metadata)
        self._save_index()
        self._save_metadata()

        # Return FAISS IDs of inserted vectors (starts at previous index size)
        start_id = len(self.metadata) - len(embeddings)
        return list(range(start_id, start_id + len(embeddings)))

    def search(self, query_vector: np.ndarray, k: int = 5):
        distances, indices = self.index.search(query_vector, k)
        results = [(self.metadata[i], distances[0][j]) for j, i in enumerate(indices[0])]
        return results

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)

    def _save_metadata(self):
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def _load_metadata(self):
        with open(self.metadata_path, "rb") as f:
            return pickle.load(f)
